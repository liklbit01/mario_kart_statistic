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

    def get_timeline(self, df: pd.DataFrame) -> pd.DataFrame:
        df_event = df[df["event"].notna()].copy()

        result = pd.DataFrame({
            "player": df_event["player"],

            "time": df_event["time"].map(
                lambda x: x.get("value") if isinstance(x, dict) else None
            ),

            "event": df_event["event"].map(
                lambda x: x.get("type") if isinstance(x, dict) else None
            )
        })

        result["event_detail"] = df_event.apply(self._extract_event_detail, axis=1)
        return result.reset_index(drop=True)

    def _extract_event_detail(self, row: pd.Series) -> str:
        event = row["event"]

        if not(isinstance(event, dict)):
            return ""

        match event["type"]:
            case "charge_jump" | "jump":
                return str(event["direction"])

            case "coin_lose":
                return str(event["coin"])

            case "collision":
                return str(event["player"]) if event["cause"] == "player" else str(event["cause"])

            case "drift":
                return "" if (event["is_correct_direction"]) else "wrong direction"

            case "charge_spark" | "drift_spark" | "wall_ride_spark":
                return f'level {event["level"]}'

            case "finish":
                return str(event["rank"])

            case "flattening":
                return str(event["player"]) if (event["is_effect"]) else "(no effect)"

            case "item_block":
                return f'{event["item"]} block {event["block"]}'

            case "item_decide":
                return ",".join(
                    f'[{",".join(str(item.get("item")) for item in items if "item" in item)}]'
                    for items in event["items"]
                )

            case "item_get" | "item_roll":
                return str(event["number"])

            case "item_lose" | "item_use":
                return str(event["item"])

            case "rocket_start":
                return str(event["distance"])

            case "slipstream" | "slipstream_boost":
                return str(event["player"])

            case "spinout":
                return str(event["cause"]) if event["is_effect"] else "(no effect)"

            case _:
                return ""