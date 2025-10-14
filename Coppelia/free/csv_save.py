
import csv
from datetime import datetime

def set_csv_header(Japan_time):
    with open(
    f"data_distance{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
    mode="a",
    newline="",
    encoding="utf-8",
) as file_x:
        writer = csv.writer(file_x)
        writer.writerow(
        ["Time", "Agent[1]", "Agent[2]", "Agent[3]", "Agent[4]", "Agent[5]", "Agent[6]"]
    )
    with open(
    f"data_angular_distance{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
    mode="a",
    newline="",
    encoding="utf-8",
) as file_y:
        writer = csv.writer(file_y)
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
    with open(
    f"data_omega{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
    mode="a",
    newline="",
    encoding="utf-8",
) as file_z:
        writer = csv.writer(file_z)
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
    with open(
    f"e_i_1{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
    mode="a",
    newline="",
    encoding="utf-8",
) as ei1:
        writer = csv.writer(ei1)
        writer.writerow(
        ["Time", "Agent[1]", "Agent[2]", "Agent[3]", "Agent[4]", "Agent[5]", "Agent[6]"]
    )
    with open(
    f"e_i_2{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
    mode="a",
    newline="",
    encoding="utf-8",
) as ei2:
        writer = csv.writer(ei2)
        writer.writerow(
        ["Time", "Agent[1]", "Agent[2]", "Agent[3]", "Agent[4]", "Agent[5]", "Agent[6]"]
    )

def save_csv_data(Japan_time , current_time , ro_i , alpha_i , omega_i , e_i_1 , e_i_2):
    with open(
                f"data_distance{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
                mode="a",
                newline="",
                encoding="utf-8",
            ) as file_x:
        writer = csv.writer(file_x)
        writer.writerow(
                    [
                        current_time,
                        ro_i[0],
                        ro_i[1],
                        ro_i[2],
                        ro_i[3],
                        ro_i[4],
                        ro_i[5],
                    ]
                )  # データをCSVに書き込む
    with open(
                f"data_angular_distance{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
                mode="a",
                newline="",
                encoding="utf-8",
            ) as file_y:
        writer = csv.writer(file_y)
        writer.writerow(
                    [
                        current_time,
                        alpha_i[0],
                        alpha_i[1],
                        alpha_i[2],
                        alpha_i[3],
                        alpha_i[4],
                        alpha_i[5],
                    ]
                )  # データをCSVに書き込む
    with open(
                f"data_omega{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
                mode="a",
                newline="",
                encoding="utf-8",
            ) as file_z:
        writer = csv.writer(file_z)
        writer.writerow(
                    [
                        current_time,
                        omega_i[0],
                        omega_i[1],
                        omega_i[2],
                        omega_i[3],
                        omega_i[4],
                        omega_i[5],
                    ]
                )  # データをCSVに書き込む
    
    with open(
                f"e_i_1{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
                mode="a",
                newline="",
                encoding="utf-8",
            ) as ei1:
        writer = csv.writer(ei1)
        writer.writerow(
                    [
                        current_time,
                        e_i_1[0],
                        e_i_1[1],
                        e_i_1[2],
                        e_i_1[3],
                        e_i_1[4],
                        e_i_1[5],
                    ]
                )  # データをCSVに書き込む
    with open(
                f"e_i_2{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
                mode="a",
                newline="",
                encoding="utf-8",
            ) as ei2:
        writer = csv.writer(ei2)
        writer.writerow(
                    [
                        current_time,
                        e_i_2[0],
                        e_i_2[1],
                        e_i_2[2],
                        e_i_2[3],
                        e_i_2[4],
                        e_i_2[5],
                    ]
                )  # データをCSVに書き込む