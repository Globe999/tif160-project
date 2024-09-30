import random
from main.vision.vision import CameraDetection


def get_sorted_objects(sort_mode, order, objects):
    # Magic
    rank = {value: i for i, value in enumerate(order)}
    sorted_objects = sorted(
        objects, key=lambda x: rank.get(getattr(x, sort_mode), float("inf"))
    )

    return sorted_objects


def main():

    # Mock data generation
    types = ["circle", "square", "triangle"]
    colors = ["red", "green", "blue"]

    mock_data = []

    random.seed(8)

    for _ in range(20):
        detection = CameraDetection(
            shape=random.choice(types),
            x=random.uniform(0.0, 100.0),
            y=random.uniform(0.0, 100.0),
            z=random.uniform(0.0, 100.0),
            size=random.randint(1, 10),
            color=random.choice(colors),
        )
        mock_data.append(detection)

    sort_mode = "color"
    order = ["red", "green", "blue"]

    new_list = get_sorted_objects(sort_mode, order, mock_data)
    for i, (old, new) in enumerate(zip(mock_data, new_list)):
        print(f"{i}: {getattr(old,sort_mode)} -> {getattr(new,sort_mode)}")

    # sort_mode, order = get_instructions()

    # objects = camera.get_objects()


if __name__ == "__main__":
    main()
