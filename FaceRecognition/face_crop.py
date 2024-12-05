from PIL import Image
import numpy as np
import cv2
import os

def create_directory(path):
    """ディレクトリが存在しなければ作成する関数"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"ディレクトリを作成しました: {path}")

def read_image_pil(image_path):
    """Pillowを使用して画像を読み込み、OpenCV形式に変換する関数"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')  # RGB形式に変換
            return np.array(img)
    except Exception as e:
        print(f"Pillowで画像を読み込めませんでした: {image_path}, エラー: {e}")
        return None

def detect_and_crop_faces_single_member(input_dir, output_dir, cascade_path='haarcascade_frontalface_default.xml'):
    """
    単一のメンバーのフォルダ内の画像から顔を検出し、切り抜いて保存する関数
    
    Parameters:
    - input_dir: 入力画像が格納されているディレクトリ
    - output_dir: 切り抜いた顔画像を保存するディレクトリ
    - cascade_path: Haar CascadeのXMLファイルのパス
    """
    
    # Haar Cascadeの分類器を読み込む
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)
    if face_cascade.empty():
        raise IOError("Haar Cascade XMLファイルが読み込めません。パスを確認してください。")
    
    # 出力ディレクトリを作成
    create_directory(output_dir)
    
    # 入力ディレクトリ内の各画像ファイルを処理
    for image_name in os.listdir(input_dir):
        image_path = os.path.join(input_dir, image_name)
        print(f"処理中の画像: {image_path}")
        
        # 画像をPillowで読み込む
        img = read_image_pil(image_path)
        if img is None:
            continue
        
        # OpenCVのBGR形式に変換
        img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # グレースケールに変換
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 顔を検出
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            print(f"顔が検出されませんでした: {image_path}")
            continue
        
        # 最初に検出された顔を使用（複数顔が検出された場合）
        (x, y, w, h) = faces[0]
        face_img = img_cv[y:y+h, x:x+w]
        
        # 切り抜いた顔画像を保存
        output_path = os.path.join(output_dir, image_name)
        cv2.imwrite(output_path, face_img)
        print(f"顔を切り抜いて保存しました: {output_path}")

if __name__ == "__main__":
    # 入力データのディレクトリ（単一のメンバーのフォルダ）
    input_directory = r"C:\Users\n-nakagawa_d1\Downloads\IdolMembers\井上 梨名"  # 例: /data/メンバー名
    
    # 出力データのディレクトリ
    output_directory = r"C:\Users\n-nakagawa_d1\Desktop\Python\Sakurazaka\FaceRecognition\data\井上 梨名"  # 切り抜いた顔画像を保存する場所
    
    # 顔検出と切り抜きを実行
    detect_and_crop_faces_single_member(input_directory, output_directory)
