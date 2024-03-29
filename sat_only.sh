# 训练sun的数据集


#sat,plain
ts -G 1 python train.py \
    --model deeplabv3+ \
    --sat_dir datasets/dataset_time/train_val/image \
    --mask_dir datasets/dataset_time/train_val/mask \
    --test_sat_dir datasets/dataset_time/test/image_test \
    --test_mask_dir datasets/dataset_time/test/mask \
    --gps_dir '' \
    \
    --gps_type '' \
    --gps_render_type '' \
    --count_render_type '' \
    --epochs 60

ts -G 1 python train.py \
    --model unet \
    --sat_dir datasets/dataset_time/train_val/image \
    --mask_dir datasets/dataset_time/train_val/mask \
    --test_sat_dir datasets/dataset_time/test/image_test \
    --test_mask_dir datasets/dataset_time/test/mask \
    --gps_dir '' \
    \
    --gps_type '' \
    --gps_render_type '' \
    --count_render_type '' \
    --epochs 60

ts -G 2 python train.py \
    --model resunet \
    --sat_dir datasets/dataset_time/train_val/image \
    --mask_dir datasets/dataset_time/train_val/mask \
    --test_sat_dir datasets/dataset_time/test/image_test \
    --test_mask_dir datasets/dataset_time/test/mask \
    --gps_dir '' \
    \
    --gps_type '' \
    --gps_render_type '' \
    --count_render_type '' \
    --epochs 60

ts -G 1 python train.py \
    --model linknet \
    --sat_dir datasets/dataset_time/train_val/image \
    --mask_dir datasets/dataset_time/train_val/mask \
    --test_sat_dir datasets/dataset_time/test/image_test \
    --test_mask_dir datasets/dataset_time/test/mask \
    --gps_dir '' \
    \
    --gps_type '' \
    --gps_render_type '' \
    --count_render_type '' \
    --epochs 60

ts -G 1 python train.py \
    --model dlink34 \
    --sat_dir datasets/dataset_time/train_val/image \
    --mask_dir datasets/dataset_time/train_val/mask \
    --test_sat_dir datasets/dataset_time/test/image_test \
    --test_mask_dir datasets/dataset_time/test/mask \
    --gps_dir '' \
    \
    --gps_type '' \
    --gps_render_type '' \
    --count_render_type '' \
    --epochs 60

ts -G 1 python train.py \
    --model dlink34_1d \
    --sat_dir datasets/dataset_time/train_val/image \
    --mask_dir datasets/dataset_time/train_val/mask \
    --test_sat_dir datasets/dataset_time/test/image_test \
    --test_mask_dir datasets/dataset_time/test/mask \
    --gps_dir '' \
    \
    --gps_type '' \
    --gps_render_type '' \
    --count_render_type '' \
    --epochs 60