import glob
import json
import pandas as pd

class MarioKartReport:
    def read_json(self) -> pd.DataFrame:
        json_list = []

        for file in glob.glob("../mario_kart_log/20250906_mario_kart_world_challenge_2025/parent_child/round_1/group_1/track_1/laps/*.ndjson"):
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    json_list.append(json.loads(line))

        return pd.DataFrame(json_list)