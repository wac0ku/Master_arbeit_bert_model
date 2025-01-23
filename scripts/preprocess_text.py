# preprocess_text.py
import os
import re
import gc
import psutil
from typing import Optional, Dict
from pathlib import Path
import chardet
from langdetect import detect, DetectorFactory, LangDetectException
from logging_progress import setup_logger, display_progress


# Für konsistente Spracherkennung
DetectorFactory.seed = 0
logger = setup_logger("preprocess_text")

# EASA-spezifische Whitelist
EASA_TERMS = {
    "FOD-resistant", "TCAS-II", "EGPWS", "PART-145", "AMC-20",
    "CS-25", "EASA-SIB", "RVSM", "ACAS-Xu", "SMS-CAA"
}

class TextPreprocessor:
    """EASA-konformer Textpreprozessor mit Memory-Management"""
    
    def __init__(self):
        self.memory_warning_threshold = 1024 * 1024 * 100  # 100MB
        
    def _clean_text(self, text: str) -> str:
        """Textbereinigung unter Erhaltung technischer Begriffe"""
        # Erhalte Bindestriche in technischen Begriffen
        text = re.sub(r'(?<!\w)([^\w\s-]+)|([^\w\s-])(?!\w)', '', text)
        
        # Erhalte EASA-spezifische Terminologie
        for term in EASA_TERMS:
            text = text.replace(term, term.replace('-', 'HYPHEN'))
            
        # Entferne spezielle Zeichen
        text = re.sub(r'[^\w\s-]', '', text)
        
        # Wiederherstellung der Originalbegriffe
        for term in EASA_TERMS:
            text = text.replace(term.replace('-', 'HYPHEN'), term)
            
        return re.sub(r'\s+', ' ', text).strip()

    def _detect_encoding(self, file_path: str) -> Optional[str]:
        """Automatische Kodierungserkennung mit Sicherheitschecks"""
        try:
            with open(file_path, 'rb') as f:
                rawdata = f.read(10000)
                result = chardet.detect(rawdata)
                return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
        except Exception as e:
            logger.error(f"Encoding detection failed: {e}")
            return None

    def _check_memory(self) -> bool:
        """Memory-Check vor großen Dateien"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss < self.memory_warning_threshold

    def _process_single_file(self, input_path: Path, output_path: Path) -> Dict[str, str]:
        """Verarbeitet einzelne Datei mit EASA-Standards"""
        metadata = {'filename': input_path.name, 'status': 'failed'}
        
        try:
            if not self._check_memory():
                logger.warning("High memory usage - triggering GC")
                gc.collect()

            # Kodierungserkennung
            encoding = self._detect_encoding(input_path)
            if not encoding:
                raise ValueError("Invalid file encoding")

            # Datei einlesen mit Progress-Monitoring
            with open(input_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()

            # EASA-Validierung
            if len(content) < 100:
                raise ValueError("File too short for EASA compliance")

            cleaned_text = self._clean_text(content)
            
            # Spracherkennung mit Fallback
            try:
                lang = detect(cleaned_text[:1000]) if len(cleaned_text) > 50 else 'en'
            except LangDetectException:
                lang = 'en'

            # Speichern der bereinigten Daten
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)

            metadata.update({
                'status': 'success',
                'encoding': encoding,
                'language': lang,
                'original_size': len(content),
                'processed_size': len(cleaned_text)
            })
            
            logger.info(f"Processed {input_path.name} | Lang: {lang} | "
                       f"Compression: {len(cleaned_text)/len(content):.1%}")

            return metadata

        except Exception as e:
            logger.error(f"Error processing {input_path.name}: {str(e)}")
            metadata['error'] = str(e)
            return metadata

    def preprocess_txt(self, input_dir: str, output_dir: str) -> Dict[str, Dict]:
        """Batch-Verarbeitung mit EASA-Compliance-Checks"""
        results = {}
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        output_path.mkdir(parents=True, exist_ok=True)

        files = [f for f in input_path.glob('*.txt') if f.is_file()]
        
        for file in display_progress(files, description="Processing EASA Files"):
            result = self._process_single_file(
                file,
                output_path / file.name
            )
            results[file.name] = result

            # Memory-Sicherheit
            if (files.index(file) + 1) % 10 == 0:
                gc.collect()

        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        logger.info(f"Processing complete | Success: {success_count}/{len(files)}")
        return results

# Kommandozeileninterface für Produktionseinsatz
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="EASA-Compliant Text Preprocessor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input", type=str, required=True,
                        help="Input directory with raw text files")
    parser.add_argument("--output", type=str, required=True,
                        help="Output directory for processed files")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()
    
    logger.setLevel(args.log_level)
    processor = TextPreprocessor()
    processor.preprocess_txt(args.input, args.output)