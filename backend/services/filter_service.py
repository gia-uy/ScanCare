
"""Điều phối các bộ lọc có sẵn của An."""

from modules.filtering import median_filter, gaussian_filter

FILTER_LEVELS = {
    "nhe": 3,
    "vua": 5,
    "manh": 7,
}


def apply_selected_filter(
    image,
    apply_filter=False,
    filter_method="median",
    filter_level="nhe",
):
    if not apply_filter:
        return image, []

    if filter_method not in ("median", "gaussian"):
        raise ValueError(
            "filter_method phải là median hoặc gaussian"
        )

    if filter_level not in FILTER_LEVELS:
        raise ValueError(
            "filter_level phải là nhe, vua hoặc manh"
        )

    kernel_size = FILTER_LEVELS[filter_level]

    if filter_method == "median":
        result = median_filter(
            image,
            kernel_size=kernel_size
        )
    else:
        result = gaussian_filter(
            image,
            kernel_size=kernel_size,
            sigma=0
        )

    steps = [{
        "method": f"{filter_method}_filter",
        "kernel_size": kernel_size,
        "level": filter_level
    }]

    return result, steps
