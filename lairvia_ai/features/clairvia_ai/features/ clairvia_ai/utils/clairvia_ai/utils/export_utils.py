import logging
from typing import Dict, Any
from pathlib import Path
from io import BytesIO

logger = logging.getLogger(__name__)

class ExportManager:
    """Export notes and artifacts to various formats"""
    
    def __init__(self):
        self.logger = logger
    
    def export(self, content: Dict[str, Any], format_type: str, output_path: str):
        """
        Export content to the specified format.
        Supported: txt, json, pdf
        """
        fmt = format_type.lower()
        if fmt == "txt":
            return self._export_txt(content, output_path)
        elif fmt == "json":
            return self._export_json(content, output_path)
        elif fmt == "pdf":
            return self._export_pdf(content, output_path)
        else:
            self.logger.error(f"Unsupported export format: {format_type}")
            raise ValueError("Unsupported export format")
    
    def _export_txt(self, content: Dict[str, Any], output_path: str):
        try:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('w', encoding='utf-8') as f:
                for key, val in content.items():
                    f.write(f"=== {key} ===\n\n")
                    if isinstance(val, dict):
                        for subk, subv in val.items():
                            f.write(f"-- {subk} --\n")
                            f.write(str(subv) + "\n\n")
                    else:
                        f.write(str(val) + "\n\n")
            self.logger.info(f"Exported TXT to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting TXT: {e}")
            return False
    
    def _export_json(self, content: Dict[str, Any], output_path: str):
        import json
        try:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Exported JSON to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting JSON: {e}")
            return False
    
    def _export_pdf(self, content: Dict[str, Any], output_path: str):
        # Use reportlab for PDF export
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
        except ImportError:
            self.logger.error("reportlab not installed. Install with: pip install reportlab")
            raise
        
        try:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            c = canvas.Canvas(str(p), pagesize=A4)
            width, height = A4
            margin = 20 * mm
            x = margin
            y = height - margin
            line_height = 10 * mm / 3.0
            
            def write_block(text_block: str):
                nonlocal x, y
                for paragraph in str(text_block).split("\n"):
                    lines = self._wrap_text(paragraph, int((width - 2*margin) / (6 * mm)))
                    for line in lines:
                        if y < margin + line_height:
                            c.showPage()
                            y = height - margin
                        c.drawString(x, y, line)
                        y -= line_height
            
            for key, val in content.items():
                title = f"=== {key} ==="
                write_block(title + "\n")
                if isinstance(val, dict):
                    for subk, subv in val.items():
                        write_block(f"-- {subk} --\n")
                        write_block(str(subv) + "\n\n")
                else:
                    write_block(str(val) + "\n\n")
            
            c.save()
            self.logger.info(f"Exported PDF to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting PDF: {e}")
            return False
    
    def _wrap_text(self, text: str, max_chars: int) -> list:
        """Basic text wrapper"""
        words = text.split()
        lines = []
        current = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 > max_chars:
                lines.append(" ".join(current))
                current = [w]
                cur_len = len(w)
            else:
                current.append(w)
                cur_len += len(w) + 1
        if current:
            lines.append(" ".join(current))
        return lines
