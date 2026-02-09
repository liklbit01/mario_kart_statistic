from mario_kart_report import MarioKartReport

def main() -> None:
    report = MarioKartReport()
    df = report.read_json()

if __name__ == "__main__":
    main()