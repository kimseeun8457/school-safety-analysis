import os
import pandas as pd

def main():
    excel_path = input("엑셀 파일 경로를 입력하세요: ").strip().strip('"')

    if not os.path.exists(excel_path):
        print("❌ 파일을 찾을 수 없습니다.")
        return

    try:
        xls = pd.ExcelFile(excel_path)

        print("\n=== 시트 목록 ===")
        for sheet in xls.sheet_names:
            print(f"- {sheet}")

        sheet_input = input(
            "\n변환할 시트명을 입력하세요 (여러 개는 쉼표로 구분): "
        )

        # 입력한 시트명 리스트
        sheet_names = [s.strip() for s in sheet_input.split(",")]

        output_dir = os.path.dirname(excel_path)

        print()

        for sheet_name in sheet_names:
            if sheet_name not in xls.sheet_names:
                print(f"⚠️ '{sheet_name}' 시트는 존재하지 않습니다. 건너뜁니다.")
                continue

            df = pd.read_excel(excel_path, sheet_name=sheet_name)

            safe_name = "".join(
                c if c not in r'\/:*?"<>|' else "_" for c in sheet_name
            )

            csv_path = os.path.join(output_dir, f"{safe_name}.csv")

            df.to_csv(csv_path, index=False, encoding="utf-8-sig")

            print(f"✅ {sheet_name} → {csv_path}")

        print("\n🎉 선택한 시트 변환이 완료되었습니다.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()