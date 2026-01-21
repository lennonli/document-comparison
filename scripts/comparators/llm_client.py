
import os
import json
import logging
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        self.model = os.getenv("LLM_MODEL") or "gpt-4o"
        
        self.client = None
        if self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            print("⚠️ LLM API Key not found or OpenAI lib missing. Formatting check pending.")

    def is_available(self):
        return self.client is not None

    def compare_sections(self, text_a, text_b, section_name=""):
        if not self.client:
            return None

        prompt = f"""
        你是一位专业的IPO律师助手。请对比以下两段关于“{section_name}”的文本，找出实质性的业务差异（如主体变更、金额、时间、权利义务、关联关系等）。
        忽略格式修饰、标点符号和单纯的措辞优化。
        
        如果发现实质差异，请按以下 JSON 格式输出：
        {{
            "has_diff": true,
            "summary": "一句话概括差异本质",
            "details": [
                {{"item": "差异点1 (如: 关联方名单)", "doc_a": "描述A", "doc_b": "描述B", "risk": "潜在风险"}}
            ]
        }}
        如果无实质差异，仅输出 {{"has_diff": false}}。
        
        文本A：
        {text_a[:4000]} 
        (截断...)
        
        文本B：
        {text_b[:4000]}
        (截断...)
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise legal document assistant. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
