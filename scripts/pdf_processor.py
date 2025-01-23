from pathlib import Path
import pdfplumber
from typing import Dict
from datetime import datetime
from logging_progress import console

class EASAPdfProcessor:
    """EASA-konformer PDF-Prozessor für Masterarbeit"""
    
    EASA_KEYWORDS = {
        "incident", "maintenance", "part-145", 
        "safety recommendation", "airworthiness"
    }

    def process_batch(self, input_dir: Path, output_dir: Path) -> Dict:
        """Batch-Verarbeitung von PDF-Dateien"""
        results = {}
        for pdf_file in input_dir.glob("*.pdf"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"{pdf_file.stem}_analysis_{timestamp}.txt"
            results[pdf_file.name] = self._process_single(pdf_file, output_path)
        return results

    def _process_single(self, pdf_file: Path, output_path: Path) -> Dict:
        """Verarbeite einzelne PDF-Datei"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with pdfplumber.open(pdf_file) as pdf:
                content = "\n".join(
                    f"Seite {page.page_number}:\n{page.extract_text()}\n"
                    for page in pdf.pages
                )
                
                keyword_count = sum(
                    1 for keyword in self.EASA_KEYWORDS
                    if keyword in content.lower()
                )

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"EASA-Analysebericht - Masterarbeit\n")
                    f.write(f"Originaldatei: {pdf_file.name}\n")
                    f.write(f"Analysezeitpunkt: {datetime.now().isoformat()}\n")
                    f.write(f"Gefundene Schlüsselwörter: {keyword_count}\n")
                    f.write("\nInhaltsanalyse:\n")
                    f.write(content)

            return {
                "status": "success",
                "easa_keywords": keyword_count,
                "output_path": str(output_path)
            }

        except Exception as e:
            console.print(f"[red]Fehler bei {pdf_file.name}: {str(e)}")
            return {
                "status": "failed",
                "easa_keywords": 0,
                "output_path": None
            }