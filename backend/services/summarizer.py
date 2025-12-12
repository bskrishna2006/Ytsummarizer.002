import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class SummarizerService:
    """Service for generating AI-powered summaries using Groq LLaMA"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise Exception("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key.strip())
    
    def chunk_text(self, text: str, max_chars: int = 2500) -> list:
        """
        Split text into smaller chunks to avoid token limits
        
        Args:
            text: Text to chunk
            max_chars: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_chars and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def summarize(
        self,
        text: str,
        summary_type: str = "general",
        chunk_size: int = 2500,
        max_tokens: int = 500
    ) -> str:
        """
        Summarize text using Groq's LLaMA model with chunking for large texts
        
        Args:
            text: Text to summarize
            summary_type: Type of summary (general, detailed, bullet_points, key_takeaways)
            chunk_size: Maximum characters per chunk
            max_tokens: Maximum tokens for summary generation
            
        Returns:
            Generated summary text
        """
        # Check if text is too long and needs chunking
        if len(text) > 3000:
            chunks = self.chunk_text(text, max_chars=chunk_size)
            chunk_summaries = []
            
            for i, chunk in enumerate(chunks):
                try:
                    # Summarize each chunk
                    prompt = f"Please provide a concise summary of this part of a video transcript:\n\n{chunk}"
                    
                    response = self.client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=min(300, max_tokens // 2),
                        temperature=0.1
                    )
                    
                    chunk_summaries.append(response.choices[0].message.content)
                    
                except Exception as e:
                    raise Exception(f"Error summarizing chunk {i+1}: {str(e)}")
            
            # Combine all chunk summaries
            combined_summary = "\n\n".join(chunk_summaries)
            
            # Create final summary from combined chunks
            final_prompts = {
                "general": f"Please create a cohesive summary from these section summaries of a video:\n\n{combined_summary}",
                "detailed": f"Please create a detailed, well-structured summary from these section summaries:\n\n{combined_summary}",
                "bullet_points": f"Please organize these section summaries into clear bullet points:\n\n{combined_summary}",
                "key_takeaways": f"Please extract the main insights and key takeaways from these summaries:\n\n{combined_summary}"
            }
            
            try:
                final_response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "user", "content": final_prompts[summary_type]}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.1
                )
                
                return final_response.choices[0].message.content
                
            except Exception as e:
                # If final summary fails, return the combined chunk summaries
                return combined_summary
        
        else:
            # Original logic for shorter texts
            prompts = {
                "general": f"Please provide a clear and concise summary of the following video transcript:\n\n{text}",
                "detailed": f"Please provide a detailed summary with key points and main topics from the following video transcript:\n\n{text}",
                "bullet_points": f"Please summarize the following video transcript in bullet points, highlighting the main topics:\n\n{text}",
                "key_takeaways": f"Please extract the key takeaways and main insights from the following video transcript:\n\n{text}"
            }
            
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "user", "content": prompts[summary_type]}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.1
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                raise Exception(f"Error generating summary: {str(e)}")
