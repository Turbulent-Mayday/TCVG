import random
from collections import deque

import numpy as np
import PIL.Image
import pytest

VALID_RESOLUTIONS = {
    "large": (496, 700),
    "small": (284, 400),
}


def generate_bfs_card(size_type: str = "large") -> np.ndarray:
    """Synthesizes procedural card artwork via stochastic Breadth-First Search (BFS) flood-filling.

    Seeds a random origin pixel with an initial RGB vector and propagates outward across an
    8-connected Moore neighborhood. Neighboring pixel colors are derived by applying a 3D Gaussian
    random walk (zero mean, low variance) with rare uniform mutations to simulate organic,
    continuous color gradients while strictly preventing zero-distance static clones.
    """
    if size_type not in VALID_RESOLUTIONS:
        raise ValueError(
            f"Unsupported resolution preset '{size_type}'. Expected one of: {list(VALID_RESOLUTIONS.keys())}"
        )

    width, height = VALID_RESOLUTIONS[size_type]
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    visited = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    start_x = random.randint(0, width - 1)
    start_y = random.randint(0, height - 1)
    start_color = [random.randint(40, 215) for _ in range(3)]

    canvas[start_y, start_x] = start_color
    visited[start_y, start_x] = True
    queue.append((start_x, start_y))

    neighbors = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]

    while queue:
        cx, cy = queue.popleft()
        current_color = canvas[cy, cx].astype(float)

        for dx, dy in neighbors:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[ny, nx]:
                color_shift = np.random.normal(loc=0.0, scale=6.0, size=3)
                while np.all(np.round(color_shift) == 0):
                    color_shift = np.random.normal(loc=0.0, scale=6.0, size=3)

                if random.random() < 0.015:
                    color_shift += np.random.uniform(-35, 35, size=3)

                neighbor_color = np.clip(current_color + color_shift, 0, 255).astype(
                    np.uint8
                )
                canvas[ny, nx] = neighbor_color
                visited[ny, nx] = True
                queue.append((nx, ny))

    return canvas


def render_card_to_terminal(card_array: np.ndarray, preview_width: int = 40) -> None:
    """Renders an RGB numpy array directly into the terminal via ANSI 24-bit TrueColor half-blocks."""
    img = PIL.Image.fromarray(card_array)
    aspect_ratio = img.height / img.width
    preview_height = int(preview_width * aspect_ratio)
    if preview_height % 2 != 0:
        preview_height += 1

    small = np.array(
        img.resize((preview_width, preview_height), PIL.Image.Resampling.BILINEAR)
    )
    lines = [f"\n--- Synthetic Card Preview ({img.width}x{img.height}) ---"]
    for y in range(0, preview_height, 2):
        row_str = []
        for x in range(preview_width):
            r1, g1, b1 = small[y, x]
            r2, g2, b2 = small[y + 1, x]
            row_str.append(f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀")
        lines.append("".join(row_str) + "\033[0m")
    print("\n".join(lines))


@pytest.mark.parametrize(
    "size_type, expected_shape",
    [
        ("large", (700, 496, 3)),
        ("small", (400, 284, 3)),
    ],
)
def test_generate_bfs_card_resolutions(size_type, expected_shape):
    """Verifies generated tensor dimensions strictly match canonical card aspect ratios."""
    image = generate_bfs_card(size_type=size_type)
    assert image.shape == expected_shape, (
        f"Tensor shape mismatch: got {image.shape}, expected {expected_shape}"
    )
    assert image.dtype == np.uint8, (
        f"Invalid pixel buffer dtype: {image.dtype}, expected uint8"
    )


def test_generate_bfs_card_invalid_resolution():
    """Ensures non-standard resolution presets are rejected with a descriptive ValueError."""
    with pytest.raises(ValueError, match="Unsupported resolution preset"):
        generate_bfs_card(size_type="ultra_hd")


def test_generate_bfs_card_uniqueness():
    """Confirms consecutive invocations synthesize distinct stochastic canvases."""
    first_card = generate_bfs_card(size_type="small")
    second_card = generate_bfs_card(size_type="small")
    assert not np.array_equal(first_card, second_card), (
        "Generator produced two identical canvases across independent runs"
    )


def test_visual_and_save_synthetic_card(tmp_path, card_preview):
    """Confirms synthetic RGB matrices serialize cleanly to JPEG assets with intact header dimensions."""
    card_array = generate_bfs_card(size_type="large")

    card_preview(card_array)

    img = PIL.Image.fromarray(card_array)
    output_file = tmp_path / "synthetic_card_496x700.jpg"
    img.save(output_file)

    assert output_file.exists(), (
        "Failed to flush synthetic card JPEG to temporary filesystem"
    )
    with PIL.Image.open(output_file) as loaded:
        assert loaded.size == (
            496,
            700,
        ), f"Corrupted JPEG header dimensions: got {loaded.size}, expected (496, 700)"
