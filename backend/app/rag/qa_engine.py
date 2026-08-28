import logging
import os
import re
from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.rag.vector_store import vector_store
from backend.app.models.chat import ChatResponse, SourceCitation

logger = logging.getLogger(__name__)


class GroundedQAEngine:
    """RAG Question-Answering engine grounded strictly in uploaded lab manual content."""

    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY

    def answer_question(
        self,
        manual_id: str,
        query: str,
        experiment_id: Optional[str] = None,
        exp_number: Optional[int] = None,
        mode: str = "standard",
        exp_context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        # Step 1: Perform vector search for relevant document chunks
        top_chunks = vector_store.search(
            manual_id=manual_id,
            query=query,
            top_k=settings.TOP_K_RESULTS,
            experiment_number=exp_number
        )

        citations: List[SourceCitation] = []
        context_passages = []

        for chunk, score in top_chunks:
            context_passages.append(chunk["text"])
            citations.append(SourceCitation(
                manual_id=manual_id,
                experiment_number=chunk.get("experiment_number"),
                experiment_title=chunk.get("experiment_title"),
                section_name=f"Experiment {chunk.get('experiment_number')}",
                excerpt=chunk["text"][:250] + ("..." if len(chunk["text"]) > 250 else ""),
                score=round(score, 4)
            ))

        # Step 2: Inject structured DB experiment context if available
        if exp_context:
            struct_summary = (
                f"Experiment {exp_context.get('experiment_number')}: {exp_context.get('title')}\n"
                f"Aim: {exp_context.get('aim')}\n"
                f"Theory: {exp_context.get('theory')}\n"
                f"Equipment: {', '.join(exp_context.get('equipment') or [])}\n"
                f"Procedure Steps:\n" + "\n".join(f"- {s}" for s in (exp_context.get("procedure") or [])[:10]) + "\n"
                f"Safety Precautions:\n" + "\n".join(f"- {s}" for s in (exp_context.get("safety") or [])[:5]) + "\n"
                f"Troubleshooting: {exp_context.get('troubleshooting') or 'N/A'}"
            )
            context_passages.insert(0, struct_summary)
            if not citations:
                citations.append(SourceCitation(
                    manual_id=manual_id,
                    experiment_number=exp_context.get("experiment_number"),
                    experiment_title=exp_context.get("title"),
                    section_name="Structured Manual Extract",
                    excerpt=struct_summary[:250] + "...",
                    score=1.0
                ))

        combined_context = "\n\n".join(context_passages).strip()

        # Check if context was retrieved
        if not combined_context:
            return ChatResponse(
                query=query,
                answer="Information not found in the uploaded laboratory manual. Please check if the relevant experiment is present in the document.",
                mode=mode,
                grounded=False,
                manual_id=manual_id,
                experiment_id=experiment_id,
                citations=[]
            )

        # Step 3: Attempt LLM generation or Grounded Synthesis fallback
        answer = self._generate_llm_answer(query, combined_context, mode)

        return ChatResponse(
            query=query,
            answer=answer,
            mode=mode,
            grounded=True,
            manual_id=manual_id,
            experiment_id=experiment_id,
            citations=citations
        )

    def _generate_llm_answer(self, query: str, context: str, mode: str) -> str:
        # Check OpenAI key
        if self.openai_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.prompts import ChatPromptTemplate

                prompt_template = """You are an expert AI Laboratory Assistant.
Your answers MUST be strictly based on the provided laboratory manual context below.
Do not hallucinate procedures, scientific data, or safety guidelines.
If the information is not supported by the context, state clearly that it is not available in the manual.

Context:
{context}

Query: {query}
Mode: {mode}

Answer:"""
                llm = ChatOpenAI(api_key=self.openai_key, model="gpt-3.5-turbo", temperature=0.2)
                prompt = ChatPromptTemplate.from_template(prompt_template)
                chain = prompt | llm
                res = chain.invoke({"context": context, "query": query, "mode": mode})
                return res.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI LLM invocation failed: {e}. Falling back to Grounded Synthesis Reader.")

        # Fallback Grounded Synthesizer (works without API key)
        return self._synthesize_grounded_answer(query, context, mode)

    def _synthesize_grounded_answer(self, query: str, context: str, mode: str) -> str:
        q_lower = query.lower()

        if "aim" in q_lower or "objective" in q_lower:
            m = re.search(r'aim:\s*(.*?)(?=\n|theory|equipment|$)', context, re.IGNORECASE)
            if m:
                return f"**Aim of Experiment:**\n{m.group(1).strip()}"

        if "procedure" in q_lower or "step" in q_lower or "how to" in q_lower:
            m = re.search(r'Procedure Steps:\n(.*?)(?=\n[A-Z]|\Z)', context, re.DOTALL | re.IGNORECASE)
            if m:
                return f"**Step-by-Step Procedure (from Manual):**\n\n{m.group(1).strip()}"

        if "theory" in q_lower or "explain" in q_lower:
            m = re.search(r'theory:\s*(.*?)(?=\n[A-Z]|\Z)', context, re.DOTALL | re.IGNORECASE)
            theory_text = m.group(1).strip() if m else context[:600]
            if mode == "simple_explanation":
                return f"**Simple Explanation of Theory:**\n\n{theory_text}\n\n*Key Practical Takeaway:* Follow the manual procedures carefully and record observed measurements."
            return f"**Experiment Theory:**\n\n{theory_text}"

        if "equipment" in q_lower or "apparatus" in q_lower or "tools" in q_lower:
            m = re.search(r'equipment:\s*(.*?)(?=\n|procedure|$)', context, re.IGNORECASE)
            if m:
                return f"**Equipment / Apparatus Required:**\n\n{m.group(1).strip()}"

        if "safety" in q_lower or "precaution" in q_lower or "warning" in q_lower:
            m = re.search(r'Safety Precautions:\n(.*?)(?=\n[A-Z]|\Z)', context, re.DOTALL | re.IGNORECASE)
            if m:
                return f"**Safety Precautions & Guidelines:**\n\n{m.group(1).strip()}\n\n⚠️ Always conduct experiments under proper laboratory supervision."

        if "troubleshoot" in q_lower or "error" in q_lower or "wrong" in q_lower or "expected" in q_lower:
            return (
                f"**Troubleshooting & Common Causes:**\n\n"
                f"Based on the manual content:\n- Ensure all equipment connections and calibrations are correct.\n"
                f"- Check standard precautions and step execution sequence.\n"
                f"- Refer to manual observations for expected tolerances."
            )

        # Default grounded answer summary
        return f"**Manual Excerpt & Grounded Information:**\n\n{context[:700]}...\n\n*(Sourced directly from uploaded laboratory manual)*"


qa_engine = GroundedQAEngine()
