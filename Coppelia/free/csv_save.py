
import csv

def set_csv_header(Japan_time , nam):
    with open(
    f"name[{nam}]{Japan_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv",
    mode="a",
    newline="",
    encoding="utf-8",
) as nm:
        writer = csv.writer(nm)
        writer.writerow(
        ["Time", "Agent[1]", "Agent[2]", "Agent[3]", "Agent[4]", "Agent[5]", "Agent[6]"]
    )

def save_csv_data(Japan_time , current_time , name , nam):
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