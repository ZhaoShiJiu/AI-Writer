import re


class NovelChunker:
    """按剧情事件切分小说文本，而非机械按 token 切分"""

    def chunk_by_paragraphs(self, content: str, max_chars: int = 2000) -> list[dict]:
        """按段落切分，保持剧情完整性"""
        paragraphs = re.split(r"\n\n+", content.strip())
        chunks = []
        current_chunk = ""
        current_paragraphs = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) > max_chars and current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "paragraph_count": len(current_paragraphs),
                })
                current_chunk = para
                current_paragraphs = [para]
            else:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para
                current_paragraphs.append(para)

        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "paragraph_count": len(current_paragraphs),
            })

        return chunks

    def chunk_chapter(self, title: str, content: str, chapter_id: int, max_chars: int = 2000) -> list[dict]:
        """切分章节内容，附带元数据"""
        chunks = self.chunk_by_paragraphs(content, max_chars)
        for i, chunk in enumerate(chunks):
            chunk["chapter_id"] = chapter_id
            chunk["chapter_title"] = title
            chunk["chunk_index"] = i
        return chunks

    def extract_events(self, content: str) -> list[str]:
        """提取关键剧情事件标题"""
        events = []
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 寻找可能的剧情转折点
            if any(kw in line for kw in ["突然", "这时", "就在", "忽然", "正当", "此刻"]):
                events.append(line[:100])
        return events


novel_chunker = NovelChunker()
