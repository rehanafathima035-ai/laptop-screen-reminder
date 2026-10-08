"""Rebuild a clean, full-body walk sprite from the saved animation source."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "walk_animation_source.gif"
OUTPUT = HERE / "water_reminder.gif"
FRAME_DIR = HERE / "walk_frames"
FIRST_FRAME = 15
LAST_FRAME = 36
BODY_CROP_TOP = 250  # excludes the source GIF's own bubble; the app supplies its message
SPRITE_SIZE = (280, 410)
TARGET_HEIGHT = 390
FRAME_DURATION_MS = 120


def make_walk_frames() -> list[Image.Image]:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Walking GIF source not found: {SOURCE}")

    source = Image.open(SOURCE)
    frames = []
    for index in range(FIRST_FRAME, min(LAST_FRAME, getattr(source, "n_frames", 1))):
        source.seek(index)
        full_frame = source.convert("RGBA")
        alpha = full_frame.getchannel("A")
        bounds = alpha.crop((0, BODY_CROP_TOP, full_frame.width, full_frame.height)).getbbox()
        if bounds is None:
            continue

        left, top, right, bottom = bounds
        top += BODY_CROP_TOP
        bottom += BODY_CROP_TOP
        if left <= 0 or right >= full_frame.width:
            continue

        character = full_frame.crop((left, top, right, bottom))
        scaled_width = round(character.width * TARGET_HEIGHT / character.height)
        character = character.resize((scaled_width, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", SPRITE_SIZE, (0, 0, 0, 0))
        x = (SPRITE_SIZE[0] - scaled_width) // 2
        y = SPRITE_SIZE[1] - TARGET_HEIGHT - 10
        canvas.alpha_composite(character, (x, y))
        frames.append(canvas)

    if len(frames) < 6:
        raise ValueError("Not enough full-body walking frames were found in the source GIF")
    return frames


def save_gif(frames: list[Image.Image]) -> None:
    FRAME_DIR.mkdir(exist_ok=True)
    for index, frame in enumerate(frames):
        frame.save(FRAME_DIR / f"frame_{index:03}.png", format="PNG")

    indexed = []
    for frame in frames:
        alpha = frame.getchannel("A")
        paletted = frame.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
        transparent = ImageOps.invert(alpha.point(lambda value: 255 if value > 96 else 0))
        paletted.paste(255, mask=transparent)
        palette = paletted.getpalette() or []
        palette.extend([0] * (768 - len(palette)))
        paletted.putpalette(palette[:768])
        indexed.append(paletted)

    indexed[0].save(
        OUTPUT,
        save_all=True,
        append_images=indexed[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        transparency=255,
        disposal=2,
        optimize=False,
    )


if __name__ == "__main__":
    frames = make_walk_frames()
    save_gif(frames)
    print(f"Created {OUTPUT} with {len(frames)} full-body walk frames")
