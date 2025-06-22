from DSTVParser.parsers.nc_file_parser import NCFileParser
from DSTVParser.parsers.nc1_file_parser import NC1FileParser
from DSTVParser.parsers.dstv_file_parser import DSTVFileParser

class NCFileParserFactory:
    """Factory per creare il parser appropriato in base all'estensione del file"""
    @staticmethod
    def create_parser(filename: str) -> DSTVFileParser:
        """Crea il parser appropriato in base all'estensione del file"""
        if filename.lower().endswith('.nc'):
            return NCFileParser(filename)
        elif filename.lower().endswith('.nc1'):
            return NC1FileParser(filename)
        else:
            raise ValueError(f"Formato file non supportato: {filename}")
        
