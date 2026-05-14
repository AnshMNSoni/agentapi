"""Test UUID-based conversation isolation in InMemoryMemory."""

import pytest
from agentapi import InMemoryMemory, create_conversation_id


def test_auto_generated_conversation_id():
    """InMemoryMemory auto-generates conversation_id if not provided."""
    mem = InMemoryMemory()
    assert mem.conversation_id is not None
    assert len(mem.conversation_id) == 36  # UUID hex string length


def test_explicit_conversation_id():
    """InMemoryMemory accepts explicit conversation_id."""
    conv_id = create_conversation_id()
    mem = InMemoryMemory(conversation_id=conv_id)
    assert mem.conversation_id == conv_id


def test_conversation_isolation():
    """Different conversation_ids maintain separate message histories."""
    conv_id_1 = create_conversation_id()
    conv_id_2 = create_conversation_id()

    # Create two separate memory instances with different conversation IDs
    mem1 = InMemoryMemory(conversation_id=conv_id_1)
    mem2 = InMemoryMemory(conversation_id=conv_id_2)

    # Add messages to each conversation
    mem1.add({"role": "user", "content": "Hello from conversation 1"})
    mem2.add({"role": "user", "content": "Hello from conversation 2"})

    # Verify isolation: each conversation only sees its own messages
    assert len(mem1.messages) == 1
    assert len(mem2.messages) == 1
    assert mem1.messages[0]["content"] == "Hello from conversation 1"
    assert mem2.messages[0]["content"] == "Hello from conversation 2"


def test_multiple_agents_same_conversation():
    """Separate InMemoryMemory instances do not share state, even with the same conversation_id."""
    shared_conv_id = create_conversation_id()

    # Two memory instances using the SAME conversation_id remain isolated.
    mem_a = InMemoryMemory(conversation_id=shared_conv_id)
    mem_b = InMemoryMemory(conversation_id=shared_conv_id)

    # Add message via mem_a
    mem_a.add({"role": "user", "content": "Message from A"})

    assert len(mem_a.messages) == 1
    assert len(mem_b.messages) == 0
    assert mem_a.conversation_id == mem_b.conversation_id
    assert mem_a.conversation_id == shared_conv_id


def test_reset_preserves_isolation():
    """Resetting one conversation doesn't affect others."""
    conv_id_1 = create_conversation_id()
    conv_id_2 = create_conversation_id()

    mem1 = InMemoryMemory(conversation_id=conv_id_1)
    mem2 = InMemoryMemory(conversation_id=conv_id_2)

    mem1.add({"role": "user", "content": "Msg 1"})
    mem2.add({"role": "user", "content": "Msg 2"})

    # Reset conversation 1
    mem1.reset()

    # Conversation 1 should be cleared, 2 unaffected
    assert len(mem1.messages) == 0
    assert len(mem2.messages) == 1
    assert mem2.messages[0]["content"] == "Msg 2"


def test_system_prompt_per_conversation():
    """Messages remain isolated per conversation."""
    conv_id_1 = create_conversation_id()
    conv_id_2 = create_conversation_id()

    mem1 = InMemoryMemory(conversation_id=conv_id_1)
    mem2 = InMemoryMemory(conversation_id=conv_id_2)

    mem1.add({"role": "user", "content": "You are helpful"})
    mem2.add({"role": "user", "content": "You are strict"})

    assert mem1.messages[0]["content"] == "You are helpful"
    assert mem2.messages[0]["content"] == "You are strict"


def test_invalid_uuid_raises_error():
    """Invalid conversation_id format raises ValueError."""
    with pytest.raises(ValueError):
        InMemoryMemory(conversation_id="not-a-valid-uuid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
