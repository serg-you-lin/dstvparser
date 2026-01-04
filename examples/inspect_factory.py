from pathlib import Path
from dstvparser.parsers.factory import NCFileParserFactory

if __name__ == "__main__":
    data_dir = Path(__file__).parent / "data"

    nc_path = data_dir / "722.nc"
    nc1_path = data_dir / "2501.nc1"

    nc_part = NCFileParserFactory.create_parser(nc_path)
    nc_profile = nc_part.parse()

    print("Profilo nc:")
    print(nc_profile.get_header())

    nc1_part = NCFileParserFactory.create_parser(nc1_path)
    nc1_profile = nc1_part.parse()

    print("Profilo nc1:")
    print(nc1_profile.get_header())