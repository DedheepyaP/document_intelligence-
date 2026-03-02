import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from app.services.rag_service import _rephrase_chain

async def test_rephrasing():

    fake_history = [
        HumanMessage(content="What are the benefits of a savings account?"),
        AIMessage(content="Savings accounts offer interest on deposits and safety for your funds."),
        HumanMessage(content="Is there a minimum balance?"),
        AIMessage(content="Yes, most banks require a $500 minimum balance for savings accounts."),
    ]
    
    ambiguous_question = "What if it drops below that amount?"
    
    print(f"\nOriginal History")
    for msg in fake_history:
        print(f"{msg.type.capitalize()}: {msg.content}")
        
    print(f"\nAmbiguous Input")
    print(f"Human: {ambiguous_question}")
    
    print(f"\nRunning Rephrase Chain")
    result = _rephrase_chain.invoke({
        "input": ambiguous_question,
        "chat_history": fake_history
    })
    
    print(f"\n Rephrased standalone question:\n{result}\n")

if __name__ == "__main__":
    asyncio.run(test_rephrasing())
