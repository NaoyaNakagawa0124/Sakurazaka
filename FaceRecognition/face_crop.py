from PIL import Image
import numpy as np
import os
from mtcnn import MTCNN

def create_directory(path):
    """ディレクトリが存在しなければ作成する関数"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"ディレクトリを作成しました: {path}")
    else:
        print(f"ディレクトリは既に存在します: {path}")

def read_image_pil(image_path):
    """Pillowを使用して画像を読み込み、NumPy配列に変換する関数"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')  # RGB形式に変換
            return np.array(img)
    except Exception as e:
        print(f"Pillowで画像を読み込めませんでした: {image_path}, エラー: {e}")
        return None

def detect_and_crop_faces_mtcnn(input_dir, output_dir):
    """MTCNNを使用して顔を検出し、切り抜いた顔画像を保存する関数"""
    detector = MTCNN()
    member_name = os.path.basename(os.path.normpath(input_dir))  # メンバー名を取得
    member_output_dir = os.path.join(output_dir, member_name)  # メンバーごとのフォルダ作成
    create_directory(member_output_dir)

    for image_name in os.listdir(input_dir):
        image_path = os.path.join(input_dir, image_name)
        print(f"処理中の画像: {image_path}")

        img = read_image_pil(image_path)
        if img is None:
            continue

        try:
            faces = detector.detect_faces(img)
        except Exception as e:
            print(f"顔検出中にエラーが発生しました: {image_path}, エラー: {e}")
            continue

        if len(faces) == 0:
            print(f"顔が検出されませんでした: {image_path}")
            continue

        for idx, face in enumerate(faces):
            x, y, w, h = face['box']
            x, y = max(0, x), max(0, y)
            face_img = img[y:y+h, x:x+w]

            # 保存ファイル名を元のファイル名に基づき設定
            original_name = os.path.splitext(image_name)[0]
            output_filename = f"{original_name}_face_{idx}.jpg"
            output_path = os.path.join(member_output_dir, output_filename)

            try:
                if face_img is not None and face_img.size > 0:
                    # PILを使用して画像を保存 (色を保持)
                    face_image = Image.fromarray(face_img)
                    face_image.save(output_path)
                    print(f"顔を切り抜いて保存しました: {output_path}")
                else:
                    print(f"切り抜き画像が不正です: {output_filename}")
            except Exception as e:
                print(f"画像の保存中にエラーが発生しました: {output_path}, エラー: {e}")


if __name__ == "__main__":
    # 入力データのディレクトリ（単一のメンバーのフォルダ）
    input_directory = r"C:\Users\n-nakagawa_d1\Downloads\IdolMembers\森田 ひかる"  # 例: /data/メンバー名

    # 出力データのディレクトリ
    output_directory = r"C:\Users\n-nakagawa_d1\Desktop\Python\Sakurazaka\FaceRecognition\data\FaceCropData"  # 切り抜いた顔画像を保存する場所

    # 顔検出と切り抜きを実行
    detect_and_crop_faces_mtcnn(input_directory, output_directory)
