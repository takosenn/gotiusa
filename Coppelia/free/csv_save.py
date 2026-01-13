import csv
import matplotlib.pyplot as plt
import os
from parameter import Params


def set_csv_header(Japan_time, nam):
    with open(
        f"name[{nam}]{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
        mode="a",
        newline="",
        encoding="utf-8",
    ) as nm:
        writer = csv.writer(nm)
        writer.writerow(
            [
                "Time",
                "Agent[1]",
                "Agent[2]",
                "Agent[3]",
                "Agent[4]",
                "Agent[5]",
                "Agent[6]",
            ]
        )


def save_csv_data(Japan_time, current_time, name, nam):
    with open(
        f"name[{nam}]{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
        mode="a",
        newline="",
        encoding="utf-8",
    ) as nm:
        writer = csv.writer(nm)
        writer.writerow(
            [
                current_time,
                name[0],
                name[1],
                name[2],
                name[3],
                name[4],
                name[5],
            ]
        )  # データをCSVに書き込む


def plot_csv_data(Japan_time, data_names=None):
    """
    実行終了後にCSVファイルを読み込んでプロットする

    Parameters:
    -----------
    Japan_time : datetime
        CSVファイル名に使用する日時
    data_names : list of str, optional
        プロットするデータ名のリスト（例: ["ro_i", "theta", "omega_i"]）
        Noneの場合は全てのCSVファイルをプロット
    """
    if data_names is None:
        # デフォルトでプロットするデータ
        data_names = [
            "ro_i",
            "theta",
            "alpha_i",
            "omega_i",
            "eta",
            "e_i_1",
            "e_i_2",
            "fi",
        ]

    # プロット用の設定
    num_plots = len(data_names)
    cols = 2  # 2列で表示
    rows = (num_plots + 1) // 2  # 必要な行数

    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    if num_plots == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for idx, nam in enumerate(data_names):
        csv_filename = f"name[{nam}]{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"

        # CSVファイルが存在するか確認
        if not os.path.exists(csv_filename):
            print(f"警告: {csv_filename} が見つかりません。スキップします。")
            continue

        # CSVファイルを読み込む
        time_data = []
        agent_data = [[] for _ in range(Params["num_agents"])]

        with open(csv_filename, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # ヘッダーをスキップ

            for row in reader:
                time_data.append(float(row[0]))
                for i in range(Params["num_agents"]):
                    agent_data[i].append(float(row[i + 1]))

        # プロット
        ax = axes[idx]
        for i in range(Params["num_agents"]):
            ax.plot(time_data, agent_data[i], label=f"Agent[{i}]")

        ax.set_xlabel("Time [s]")
        ax.set_ylabel(nam)
        ax.set_title(f"{nam} vs Time")
        ax.legend()
        ax.grid(True)

    # 使用しないサブプロットを非表示
    for idx in range(num_plots, len(axes)):
        fig.delaxes(axes[idx])

    plt.tight_layout()

    # 画像として保存
    plot_filename = f"plot_{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.png"
    plt.savefig(plot_filename, dpi=150)
    print(f"\nプロットを保存しました: {plot_filename}")

    # プロットを表示
    plt.show()
