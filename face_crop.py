import cv2
import os

def create_directory(path):
    """ディレクトリが存在しなければ作成する関数"""
    if not os.path.exists(path):
        os.makedirs(path)

def detect_and_crop_faces(input_dir, output_dir, cascade_path='haarcascade_frontalface_default.xml'):
    """
    指定されたディレクトリ内の画像から顔を検出し、切り抜いて保存する関数
    
    Parameters:
    - input_dir: 入力画像が格納されている親ディレクトリ
    - output_dir: 切り抜いた顔画像を保存する親ディレクトリ
    - cascade_path: Haar CascadeのXMLファイルのパス
    """
    
    # Haar Cascadeの分類器を読み込む
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)
    
    # 入力ディレクトリ内の各メンバーのフォルダを処理
    for member in os.listdir(input_dir):
        member_input_path = os.path.join(input_dir, member)
        member_output_path = os.path.join(output_dir, member)
        
        # メンバーの出力ディレクトリを作成
        create_directory(member_output_path)
        
        # メンバーのフォルダ内の各画像ファイルを処理
        for image_name in os.listdir(member_input_path):
            image_path = os.path.join(member_input_path, image_name)
            
            # 画像を読み込む
            img = cv2.imread(image_path)
            if img is None:
                print(f"画像を読み込めませんでした: {image_path}")
                continue
            
            # グレースケールに変換
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 顔を検出
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) == 0:
                print(f"顔が検出されませんでした: {image_path}")
                continue
            
            # 最初に検出された顔を使用（複数顔が検出された場合）
            (x, y, w, h) = faces[0]
            face_img = img[y:y+h, x:x+w]
            
            # 切り抜いた顔画像を保存
            output_path = os.path.join(member_output_path, image_name)
            cv2.imwrite(output_path, face_img)
            print(f"顔を切り抜いて保存しました: {output_path}")

if __name__ == "__main__":
    # 入力データのディレクトリ
    input_directory = 'data'  # 例: /data/メンバー名
    
    # 出力データのディレクトリ
    output_directory = 'cropped_data'  # 切り抜いた顔画像を保存する場所
    
    # 出力ディレクトリを作成
    create_directory(output_directory)
    
    # 顔検出と切り抜きを実行
    detect_and_crop_faces(input_directory, output_directory)
