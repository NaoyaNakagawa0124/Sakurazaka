from PIL import Image, ImageEnhance, ImageFilter
import os


def create_directory(path):
    """ディレクトリが存在しなければ作成する関数"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"ディレクトリを作成しました: {path}")
    else:
        print(f"ディレクトリは既に存在します: {path}")


def augment_image(image_path, output_dir):
    """画像に対してデータ拡張を行い保存する関数"""
    try:
        # 画像を開く
        with Image.open(image_path) as img:
            img = img.convert("RGB")  # RGB形式に変換
            basename = os.path.basename(image_path)
            base_filename, ext = os.path.splitext(basename)

            # 保存用ディレクトリを準備
            create_directory(output_dir)

            # データ拡張のパターン
            augmentations = [
                ("original", img),
                ("rotated_10", img.rotate(10)),
                ("rotated_-10", img.rotate(-10)),
                ("blurred", img.filter(ImageFilter.GaussianBlur(2))),
                ("bright", ImageEnhance.Brightness(img).enhance(1.5)),
                ("dark", ImageEnhance.Brightness(img).enhance(0.7)),
                ("flipped", img.transpose(Image.FLIP_LEFT_RIGHT)),
            ]

            # 拡張画像をそれぞれのサフィックスフォルダに保存
            for suffix, augmented_img in augmentations:
                suffix_dir = os.path.join(output_dir, suffix)  # サフィックス別のフォルダ作成
                create_directory(suffix_dir)
                output_path = os.path.join(suffix_dir, f"{base_filename}{ext}")
                augmented_img.save(output_path)
                print(f"保存しました: {output_path}")
    except Exception as e:
        print(f"画像処理中にエラーが発生しました: {image_path}, エラー: {e}")


def augment_dataset(input_dir, output_dir):
    """ディレクトリ全体に対してデータ拡張を行う関数"""
    for member_name in os.listdir(input_dir):
        member_input_dir = os.path.join(input_dir, member_name)
        member_output_dir = os.path.join(output_dir, member_name)

        if not os.path.isdir(member_input_dir):
            continue

        create_directory(member_output_dir)

        for image_name in os.listdir(member_input_dir):
            image_path = os.path.join(member_input_dir, image_name)
            augment_image(image_path, member_output_dir)


if __name__ == "__main__":
    # 入力データのディレクトリ
    input_directory = r"C:\Users\n-nakagawa_d1\Desktop\Python\Sakurazaka\FaceRecognition\data\FaceCropData"

    # 出力データのディレクトリ（拡張後の画像を保存）
    output_directory = r"C:\Users\n-nakagawa_d1\Desktop\Python\Sakurazaka\FaceRecognition\data\AugmentedFaceData"

    # データ拡張を実行
    augment_dataset(input_directory, output_directory)
