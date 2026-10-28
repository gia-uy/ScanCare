
import cv2
import os


def median_filter(image, kernel_size=3):
    """
    Median Filter: lọc nhiễu muối tiêu.

    Args:
        image: Ảnh đầu vào dạng numpy array.
        kernel_size: Kích thước kernel, phải là số lẻ và >= 3.

    Returns:
        Ảnh sau khi lọc.
    """
    if image is None:
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if not isinstance(kernel_size, int) or kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("Kernel phải là số lẻ và >= 3.")

    result = cv2.medianBlur(image, kernel_size)
    return result


def gaussian_filter(image, kernel_size=3, sigma=0):
    """
    Gaussian Filter: làm mượt ảnh, hỗ trợ giảm nhiễu Gaussian.

    Args:
        image: Ảnh đầu vào dạng numpy array.
        kernel_size: Kích thước kernel, phải là số lẻ và >= 3.
        sigma: Độ lệch chuẩn Gaussian.
               sigma=0: OpenCV tự tính sigma phù hợp.

    Returns:
        Ảnh sau khi lọc.
    """
    if image is None:
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if not isinstance(kernel_size, int) or kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("Kernel phải là số lẻ và >= 3.")

    if sigma < 0:
        raise ValueError("Sigma phải >= 0.")

    result = cv2.GaussianBlur(
        image,
        (kernel_size, kernel_size),
        sigmaX=sigma
    )
    return result


def save_image(image, output_path):
    """
    Lưu ảnh kết quả vào đường dẫn chỉ định.
    """
    if image is None:
        raise ValueError("Không có ảnh để lưu.")

    folder = os.path.dirname(output_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    success = cv2.imwrite(output_path, image)

    if not success:
        raise IOError(f"Không thể lưu ảnh tại: {output_path}")

    print(f"Đã lưu ảnh: {output_path}")


if __name__ == "__main__":
    # Đọc ảnh đầu vào
    image_path = "input_images/anhtest1.webp"
    image = cv2.imread(image_path)

    if image is None:
        print(f"Không đọc được ảnh: {image_path}")
        print("Hãy đặt ảnh test.jpg trong thư mục input_images.")
    else:
        # Median Filter
        median_result = median_filter(image, kernel_size=3)
        save_image(
            median_result,
            "output_images/median_3x3.jpg"
        )

        # Gaussian Filter
        gaussian_result = gaussian_filter(image, kernel_size=3)
        save_image(
            gaussian_result,
            "output_images/gaussian_3x3.jpg"
        )

        # Hiển thị ảnh để so sánh
        cv2.imshow("Original Image", image)
        cv2.imshow("Median Filter", median_result)
        cv2.imshow("Gaussian Filter", gaussian_result)

        print("Nhan phim bat ky tren cua so anh de ket thuc.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
