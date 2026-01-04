from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, List, Tuple

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("AndroidTeamKnowledge")

# 默认从 demo 目录读取 PDF，也支持用环境变量覆盖目录路径
BASE_DIR = Path(os.environ.get("KNOWLEDGE_BASE_DIR", Path(__file__).resolve().parent.parent))
DOC_DIR = Path(os.environ.get("KNOWLEDGE_PDF_DIR", BASE_DIR / "internal_docs"))

_TOKEN_RE = re.compile(r"[0-9A-Za-z_]+|[\u4e00-\u9fff]")
_DOCS: List[Tuple[str, str]] = []


def _extract_text(pdf_path: Path) -> str:
    # 兼容不同 PDF 解析库
    try:
        import pypdf as pdf_lib
    except Exception:  # pragma: no cover - fallback
        import PyPDF2 as pdf_lib

    reader = pdf_lib.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_text_file(text_path: Path) -> str:
    try:
        return text_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return text_path.read_text(encoding="utf-8", errors="ignore")


def _chunk_text(text: str, size: int = 800, overlap: int = 120) -> Iterable[str]:
    # 简单切分，避免单段内容过长影响召回效果
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        start = max(end - overlap, end)
    return chunks


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]


def _build_index() -> None:
    # 首次调用时构建内存索引，避免每次检索都读文件
    _DOCS.clear()
    for pdf_path in sorted(DOC_DIR.glob("*.pdf")):
        try:
            text = _extract_text(pdf_path)
        except Exception:
            continue
        for chunk in _chunk_text(text):
            _DOCS.append((pdf_path.name, chunk))
    for text_path in sorted(DOC_DIR.glob("*.txt")):
        try:
            text = _extract_text_file(text_path)
        except Exception:
            continue
        for chunk in _chunk_text(text):
            _DOCS.append((text_path.name, chunk))


def _score(query_tokens: List[str], chunk: str) -> int:
    # 朴素关键词命中计分，用于排序
    chunk_lower = chunk.lower()
    return sum(1 for token in query_tokens if token in chunk_lower)


@mcp.tool()
def search_internal_docs(query: str) -> str:
    """
    Search internal PDF docs for engineering specs and protocols.
    Trigger when users mention v2s, accessibility, or internal SDK rules.
    """
    print(f"[mcp] search_internal_docs called, query={query!r}")
    # 延迟初始化索引，启动更快
    if not _DOCS:
        _build_index()
    tokens = _tokenize(query)
    if not tokens:
        return "No query tokens found."

    ranked = sorted(
        ((name, chunk, _score(tokens, chunk)) for name, chunk in _DOCS),
        key=lambda item: item[2],
        reverse=True,
    )

    top_hits = [item for item in ranked if item[2] > 0][:3]
    if not top_hits:
        return "No relevant passages found."

    lines = []
    for name, chunk, score in top_hits:
        lines.append(f"[{name}] score={score}")
        lines.append(chunk)
        lines.append("")
    return "\n".join(lines).strip()


if __name__ == "__main__":
    print("Server running")
    mcp.run()
