import glob
import json
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.colors import ListedColormap
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
from skimage.transform import resize
from typing import cast, Dict, Sequence, Tuple

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

    def draw_timeline(self, df: pd.DataFrame) -> None:
        palette = cast(
            Sequence[Tuple[float, float, float, float]],
            cast(ListedColormap, colormaps["tab10"]).colors
        )

        y = df.groupby("time").cumcount()
        _, axis = plt.subplots()

        axis.scatter(
            df["time"],
            y,
            s=400,

            c=df["player"].map({
                player: palette[p % len(palette)]
                for p, player in enumerate(df["player"].unique())
            })
        )

        icon = self._init_icon()

        for time, index, event in zip(df["time"], y, df["event"]):
            axis.add_artist(
                AnnotationBbox(
                    OffsetImage(icon[event], zoom=0.2),
                    (time, index),
                    frameon=False
                )
            )

        plt.xticks(rotation=90)
        plt.gca().xaxis.set_major_locator(MultipleLocator(6))
        plt.show()

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

    def _init_icon(self) -> Dict[str, np.ndarray]:
        dir = "./icon/"

        icon = {
            "block": plt.imread(f"{dir}block.png"),
            "cancel": plt.imread(f"{dir}cancel.png"),
            "choose": plt.imread(f"{dir}choose.png"),
            "coin": plt.imread(f"{dir}coin.png"),
            "decide": plt.imread(f"{dir}decide.png"),
            "get": plt.imread(f"{dir}get.png"),
            "item": plt.imread(f"{dir}item.png"),
            "lose": plt.imread(f"{dir}lose.png"),
            "mushroom": plt.imread(f"{dir}mushroom.png"),
            "roll": plt.imread(f"{dir}roll.png"),
            "spark": plt.imread(f"{dir}spark.png"),
            "stop": plt.imread(f"{dir}stop.png"),
            "track": plt.imread(f"{dir}track.png")
        }

        result = {
            "boost": plt.imread(f"{dir}boost.png"),
            "charge": plt.imread(f"{dir}charge.png"),
            "collision": plt.imread(f"{dir}collision.png"),
            "drift": plt.imread(f"{dir}drift.png"),
            "finish": plt.imread(f"{dir}finish.png"),
            "flattening": plt.imread(f"{dir}flattening.png"),
            "hop": plt.imread(f"{dir}hop.png"),
            "item_use": icon["item"],
            "jump": plt.imread(f"{dir}jump.png"),
            "next_lap": plt.imread(f"{dir}next_lap.png"),
            "rail_ride": plt.imread(f"{dir}rail_ride.png"),
            "rocket_start": plt.imread(f"{dir}rocket_start.png"),
            "slipstream": plt.imread(f"{dir}slipstream.png"),
            "spinout": plt.imread(f"{dir}spinout.png"),
            "start": plt.imread(f"{dir}start.png"),
            "wall_ride": plt.imread(f"{dir}wall_ride.png")
        }

        result["charge_cancel"] = self._combine_icon(result["charge"], icon["cancel"])
        result["charge_jump"] = self._combine_icon(result["jump"], result["charge"])
        result["charge_spark"] = self._combine_icon(icon["spark"], result["charge"])
        result["charge_stop"] = self._combine_icon(result["charge"], icon["stop"])
        result["choose_track"] = self._combine_icon(icon["track"], icon["choose"])
        result["coin_get"] = self._combine_icon(icon["coin"], icon["get"])
        result["coin_lose"] = self._combine_icon(icon["coin"], icon["lose"])
        result["decide_track"] = self._combine_icon(icon["track"], icon["decide"])
        result["drift_boost"] = self._combine_icon(result["boost"], result["drift"])
        result["drift_spark"] = self._combine_icon(icon["spark"], result["drift"])
        result["drift_stop"] = self._combine_icon(icon["spark"], icon["stop"])
        result["item_block"] = self._combine_icon(icon["item"], icon["block"])
        result["item_decide"] = self._combine_icon(icon["item"], icon["decide"])
        result["item_get"] = self._combine_icon(icon["item"], icon["get"])
        result["item_lose"] = self._combine_icon(icon["item"], icon["lose"])
        result["item_roll"] = self._combine_icon(icon["item"], icon["roll"])
        result["jump_boost"] = self._combine_icon(result["boost"], result["jump"])
        result["mushroom_boost"] = self._combine_icon(result["boost"], icon["mushroom"])
        result["slipstream_boost"] = self._combine_icon(result["boost"], result["slipstream"])
        result["wall_ride_spark"] = self._combine_icon(icon["spark"], result["wall_ride"])
        result["wall_ride_stop"] = self._combine_icon(result["wall_ride"], icon["stop"])
        return result

    def _combine_icon(self, icon_main: np.ndarray, icon_sub: np.ndarray) -> np.ndarray:
        width_main, _, _ = icon_main.shape
        width_sub = int(width_main * 0.6)
        width_diff = width_main - width_sub
        result = icon_main.copy()

        result[width_diff:, width_diff:] = resize(
            icon_sub.astype(np.float32),
            (width_sub, width_sub),
            preserve_range=True,
            anti_aliasing=True
        ).astype(icon_main.dtype) # type: ignore[no-untyped-call]

        return result