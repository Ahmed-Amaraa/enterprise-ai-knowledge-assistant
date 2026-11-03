from app.processing.images.parser_process import extract_images, process_images
from app.services.image_description_service import ImageDescriptionService


def main() -> None:
	file_path = "app/tests/kmeans.pdf"

	images = extract_images(file_path, "output")
	processed_images = process_images(images)
	image_service = ImageDescriptionService()

	print(f"Extracted images: {len(processed_images)}")
	for index, image in enumerate(processed_images, start=1):
		result = image_service.describe_image(image["path"])
		print(f"\nImage {index}: {image['path']}")
		print(f"util: {result['util']}")
		print(f"text: {result['text']}")


if __name__ == "__main__":
	main()