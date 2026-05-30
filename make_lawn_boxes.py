
from pathlib import Path
import random

WORLD_IN = Path("Tools/simulation/gz/worlds/lawn.sdf")
WORLD_OUT = Path("Tools/simulation/gz/worlds/lawn_boxes.sdf")

# 박스 설정
BOX_SIZE_X = 1.0
BOX_SIZE_Y = 1.0
BOX_SIZE_Z = 1.0

# 맵에 배치할 영역. 너무 넓으면 로버/드론 시작점과 멀 수 있으니 일단 적당히.
X_MIN, X_MAX = -30.0, 30.0
Y_MIN, Y_MAX = -30.0, 30.0

# 박스 간격
GRID_STEP = 4.0

# 시작점 근처 비우기
SAFE_RADIUS = 5.0

# 랜덤 제거 비율. 0이면 모든 격자에 박스, 0.3이면 30% 정도 비움
DROP_PROB = 0.25

random.seed(42)


def make_box_model(name, x, y, z):
    return f"""
    <model name="{name}">
      <static>true</static>
      <pose>{x:.2f} {y:.2f} {z:.2f} 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>{BOX_SIZE_X} {BOX_SIZE_Y} {BOX_SIZE_Z}</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{BOX_SIZE_X} {BOX_SIZE_Y} {BOX_SIZE_Z}</size>
            </box>
          </geometry>
          <material>
            <diffuse>0.8 0.2 0.2 1</diffuse>
            <ambient>0.8 0.2 0.2 1</ambient>
          </material>
        </visual>
      </link>
    </model>
"""


def main():
    text = WORLD_IN.read_text()

    boxes = []
    idx = 0

    x = X_MIN
    while x <= X_MAX:
        y = Y_MIN
        while y <= Y_MAX:
            # 원점 주변은 비움. 드론/로버 spawn 영역 보호용.
            if (x * x + y * y) ** 0.5 < SAFE_RADIUS:
                y += GRID_STEP
                continue

            # 랜덤하게 일부 칸은 비움. 완전 격자보다 회피 실험에 자연스러움.
            if random.random() < DROP_PROB:
                y += GRID_STEP
                continue

            # z는 box 높이의 절반. 1m 박스면 z=0.5
            boxes.append(make_box_model(f"obstacle_box_{idx}", x, y, BOX_SIZE_Z / 2.0))
            idx += 1
            y += GRID_STEP
        x += GRID_STEP

    insert_text = "\n".join(boxes)

    # </world> 직전에 박스 삽입
    if "</world>" not in text:
        raise RuntimeError("Cannot find </world> in lawn.sdf")

    text = text.replace("</world>", insert_text + "\n  </world>")
    WORLD_OUT.write_text(text)

    print(f"Generated {WORLD_OUT}")
    print(f"Inserted {idx} boxes")


if __name__ == "__main__":
    main()