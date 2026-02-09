from mario_kart_report import MarioKartReport

def main() -> None:
    report = MarioKartReport()
    df = report.read_json()
    df_timeline = report.get_timeline(df)

if __name__ == "__main__":
    main()