"""
KỊCH BẢN RENDER CÁC GÓC PHỐI CẢNH NÂNG CẤP CỔNG TỰ ĐỘNG & HÀNG CAU BẰNG BLENDER CYCLES
"""
import bpy

# Danh sách các mái ngói để ẩn/hiện khi bóc mái
roof_objs = [obj for obj in bpy.data.objects if "Mai" in obj.name or "MuNgoi" in obj.name or "KimNoc" in obj.name or "BoNoc" in obj.name or "HoLo" in obj.name or "CoDiem" in obj.name]

bpy.context.scene.cycles.samples = 22
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900

render_tasks = [
    # 1. CỔNG SẮT TỰ ĐỘNG 4M, 2M SONG SẮT KÉO RA 2 BÊN, CÂY BƯỞI & CÂY LỘC VỪNG
    ("Cam_6_CongChinh", "d:/Work/Khu_Nha_Dong_Ho/blender_6_cong_chinh.png", False),

    # 2. HÀNG CÂY CAU TA TRUYỀN THỐNG TẠI KHOẢNG LÙI 2M BÊN TRÁI
    ("Cam_HangCau_Cong", "d:/Work/Khu_Nha_Dong_Ho/blender_11_hang_cau_cong.png", False),

    # 3. TỔNG THỂ & BÓC MÁI
    ("Cam_1_TongThe", "d:/Work/Khu_Nha_Dong_Ho/blender_1_tong_the_co_mai.png", False),
    ("Cam_2_BocMai", "d:/Work/Khu_Nha_Dong_Ho/blender_2_boc_mai_noi_that.png", True),

    # 4. HƯỚNG NAM & HƯỚNG ĐÔNG (NHÌN DÃY TRÁI VÀ AO CÁ VỊ TRÍ MỚI)
    ("Cam_Huong_Nam", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_nam.png", False),
    ("Cam_Huong_Dong", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_dong.png", False),
    ("Cam_5_ViewAo_PhongNgam", "d:/Work/Khu_Nha_Dong_Ho/blender_5_view_ao_ca.png", False),
]

for cam_name, output_path, hide_roofs in render_tasks:
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"!!! Không tìm thấy camera: {cam_name}")
        continue

    for ro in roof_objs:
        ro.hide_render = hide_roofs

    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = output_path
    print(f"\n==================================================")
    print(f">>> Đang render: {cam_name} -> {output_path} (Ẩn mái: {hide_roofs})")
    print(f"==================================================")
    bpy.ops.render.render(write_still=True)
    print(f">>> Đã render xong: {output_path}")

for ro in roof_objs:
    ro.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath="d:/Work/Khu_Nha_Dong_Ho/khu_nha_dong_ho.blend")
print("\n>>> TẤT CẢ CÁC HÌNH ẢNH ĐÃ RENDER THÀNH CÔNG RỰC RỠ!")
