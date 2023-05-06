import json

from score import ScoreStorageItem, storage_item_types


def readScoreFromFile(path: str) -> list[ScoreStorageItem]:
    print(f"Reading score from {path}...")

    with open(path, 'r') as f:
        serialized = json.load(f)

    score = []
    for item in serialized:
        print(f"Deserializing {item}")
        type_ = item.pop("type")
        score.append(storage_item_types[type_].deserialize(item))

    print(f"Finished, read {score}")
    return score



def saveScoreToFile(path: str, score: list[ScoreStorageItem]):
    print(f"Saving score to {path}...")

    serialized = []
    for item in score:
        print(f"Serialising {item}")
        serialized_item = item.serialize()
        if "type" in serialized_item:
            raise RuntimeError("Serialized version contains illegal \"type\"")
        serialized_item["type"] = type(item).__name__
        serialized.append(serialized_item)

    with open(path, 'w') as f:
        json.dump(serialized, f, indent=4)
    print(f"Finished, wrote {serialized}")
