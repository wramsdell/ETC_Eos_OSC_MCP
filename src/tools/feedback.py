"""
Feedback and Behavior Learning Tools

MCP tools for querying OSC feedback from Eos and learning operator behavior patterns.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
import json
from collections import Counter
from datetime import datetime, timedelta


class GetFeedbackLogInput(BaseModel):
    """Input model for querying feedback log."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    category: Optional[str] = Field(
        default=None,
        description="Filter by category: notify, error, event, user_action, selection, cue, patch, playback, other"
    )
    limit: int = Field(
        default=50,
        description="Maximum number of messages to return (1-500)",
        ge=1,
        le=500
    )


class GetOperatorInsightsInput(BaseModel):
    """Input model for getting operator behavior insights."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    time_window_minutes: int = Field(
        default=60,
        description="Look back this many minutes for patterns (1-1440)",
        ge=1,
        le=1440
    )


def register_feedback_tools(mcp, eos_client):
    """Register feedback and learning MCP tools."""

    @mcp.tool()
    async def eos_get_feedback_log(input: GetFeedbackLogInput) -> str:
        """
        Get recent OSC feedback messages from the Eos console.

        This allows you to see what the console is sending back, including
        notifications, errors, state changes, and operator actions.

        Requires OSC RX (receive) to be enabled in the client.
        """
        if not eos_client.enable_rx:
            return json.dumps({
                "success": False,
                "error": "OSC receive is not enabled. Set enable_rx=True when initializing client."
            })

        messages = eos_client.get_feedback_log(
            category=input.category,
            limit=input.limit
        )

        # Format timestamps for readability
        for msg in messages:
            dt = datetime.fromtimestamp(msg['timestamp'])
            msg['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')

        return json.dumps({
            "success": True,
            "count": len(messages),
            "category_filter": input.category or "all",
            "messages": messages
        }, indent=2)

    @mcp.tool()
    async def eos_get_recent_errors() -> str:
        """
        Get recent error messages from the Eos console.

        Errors indicate commands that failed or were not understood.
        This is valuable for learning what doesn't work.

        Requires OSC RX to be enabled.
        """
        if not eos_client.enable_rx:
            return json.dumps({
                "success": False,
                "error": "OSC receive is not enabled"
            })

        errors = eos_client.get_recent_errors(limit=20)

        for err in errors:
            dt = datetime.fromtimestamp(err['timestamp'])
            err['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')

        return json.dumps({
            "success": True,
            "error_count": len(errors),
            "errors": errors,
            "note": "These are commands or actions that the console rejected"
        }, indent=2)

    @mcp.tool()
    async def eos_get_operator_actions(limit: int = 50) -> str:
        """
        Get recent operator actions captured from OSC feedback.

        This shows what human operators are doing on the console, allowing
        you to learn from their behavior and techniques.

        Args:
            limit: Maximum number of actions to return (1-200)

        Requires OSC RX to be enabled.
        """
        if not eos_client.enable_rx:
            return json.dumps({
                "success": False,
                "error": "OSC receive is not enabled"
            })

        # Validate limit
        limit = max(1, min(limit, 200))

        actions = eos_client.get_operator_actions(limit=limit)

        for action in actions:
            dt = datetime.fromtimestamp(action['timestamp'])
            action['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')

        return json.dumps({
            "success": True,
            "action_count": len(actions),
            "actions": actions,
            "note": "These are actions performed by operators on the console"
        }, indent=2)

    @mcp.tool()
    async def eos_get_operator_insights(input: GetOperatorInsightsInput) -> str:
        """
        Analyze operator behavior to identify patterns and common workflows.

        This tool examines recent operator actions and provides insights like:
        - Most frequently used commands
        - Common command sequences
        - Timing patterns
        - Error patterns (what they tried that didn't work)

        This helps you learn new techniques and understand operator preferences.
        """
        if not eos_client.enable_rx:
            return json.dumps({
                "success": False,
                "error": "OSC receive is not enabled"
            })

        import time
        cutoff_time = time.time() - (input.time_window_minutes * 60)

        # Get all actions in time window
        all_actions = eos_client.get_operator_actions(limit=500)
        recent_actions = [a for a in all_actions if a['timestamp'] >= cutoff_time]

        # Get all feedback in time window
        all_feedback = eos_client.get_feedback_log(limit=500)
        recent_feedback = [f for f in all_feedback if f['timestamp'] >= cutoff_time]

        # Analyze patterns
        insights = {
            "time_window_minutes": input.time_window_minutes,
            "total_actions": len(recent_actions),
            "total_feedback_messages": len(recent_feedback),
        }

        # Action frequency analysis
        if recent_actions:
            action_types = [a['address'].split('/')[-1] for a in recent_actions]
            action_counter = Counter(action_types)
            insights["most_common_actions"] = [
                {"action": action, "count": count}
                for action, count in action_counter.most_common(10)
            ]

        # Error analysis
        errors = [f for f in recent_feedback if f['category'] == 'error']
        insights["error_count"] = len(errors)
        if errors:
            insights["recent_errors"] = [
                {
                    "time": datetime.fromtimestamp(e['timestamp']).strftime('%H:%M:%S'),
                    "error": str(e['args'])
                }
                for e in errors[-5:]
            ]

        # Category breakdown
        category_counts = Counter(f['category'] for f in recent_feedback)
        insights["feedback_by_category"] = dict(category_counts)

        # Timing analysis
        if len(recent_actions) >= 2:
            timestamps = [a['timestamp'] for a in recent_actions]
            timestamps.sort()
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            insights["average_seconds_between_actions"] = round(avg_interval, 2)

        # Recommendations based on patterns
        recommendations = []

        if insights.get("error_count", 0) > 5:
            recommendations.append(
                "High error rate detected. Review recent_errors to learn what syntax the operator struggled with."
            )

        if avg_interval < 2 and len(recent_actions) > 10:
            recommendations.append(
                "Operator is working rapidly. They may be using keyboard shortcuts or efficient workflows worth learning."
            )

        category_counts_dict = dict(category_counts)
        if category_counts_dict.get('cue', 0) > category_counts_dict.get('patch', 0):
            recommendations.append(
                "Operator focused on cue programming. They may have established workflows for building cues efficiently."
            )

        insights["recommendations"] = recommendations

        return json.dumps({
            "success": True,
            "insights": insights
        }, indent=2)

    @mcp.tool()
    async def eos_clear_feedback_log() -> str:
        """
        Clear all stored feedback messages and operator action logs.

        Use this to reset the learning history and start fresh.
        """
        if not eos_client.enable_rx:
            return json.dumps({
                "success": False,
                "error": "OSC receive is not enabled"
            })

        eos_client.clear_feedback_log()

        return json.dumps({
            "success": True,
            "message": "All feedback logs cleared"
        })