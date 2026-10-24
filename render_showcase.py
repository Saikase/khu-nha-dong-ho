"""
KỊCH BẢN RENDER CÁC GÓC PHỐI CẢNH NÂNG CẤP BẰNG BLENDER CYCLES
"""
import bpy

# Danh sách các mái ngói để ẩn/hiện khi bóc mái
roof_objs = [obj for obj in bpy.data.objects if "Mai" in obj.name or "MuNgoi" in obj.name or "KimNoc" in obj.name or "BoNoc" in obj.name or "HoLo" in obj.name or "CoDiem" in obj.name]

bpy.context.scene.cycles.samples = 24
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900

render_tasks = [
    # 1. Các phối cảnh cận cảnh khu vực BẾP MỞ, WC, NHÀ ĂN MÁI LÁ & HÀNH LANG KÍNH CỐI XAY CỐI GIÃ MỚI
    ("Cam_4_KyVat_NhaAn", "d:/Work/Khu_Nha_Dong_Ho/blender_4_ky_vat_nha_an.png", False), # MẶT KÍNH LẤY SÁNG rọi cối xay, cối giã & nhà ăn mái lá
    ("Cam_Bep_WC_Mo", "d:/Work/Khu_Nha_Dong_Ho/blender_9_bep_wc_mo.png", False),        # Bếp mở thôn quê, cửa WC hướng nhà ăn, hàng cây 2m
    ("Cam_NhaAn_MaiLa", "d:/Work/Khu_Nha_Dong_Ho/blender_10_nhaan_maila.png", False),    # Nhà ăn mái lá quê 7x4 không tường thoáng mát

    # 2. Phối cảnh tổng thể và bóc mái công năng
    ("Cam_1_TongThe", "d:/Work/Khu_Nha_Dong_Ho/blender_1_tong_the_co_mai.png", False),
    ("Cam_2_BocMai", "d:/Work/Khu_Nha_Dong_Ho/blender_2_boc_mai_noi_that.png", True),   # Ẩn toàn bộ mái để thấy rõ bố cục Bếp, WC, Nhà ăn, Cối xay
    
    # 3. Phối cảnh từ các hướng
    ("Cam_Huong_Tay", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_tay.png", False),     # Nhìn trực diện sang dãy phải (Bếp, WC, Nhà ăn, Chòi vuông)
    ("Cam_Huong_Nam", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_nam.png", False),     # Nhìn từ cổng chính vào khuôn viên
]

for cam_name, output_path, hide_roofs in render_tasks:
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"!!! Không tìm thấy camera: {cam_name}")
        continue

    # Đặt ẩn/hiện mái
    for ro in roof_objs:
        ro.hide_render = hide_roofs

    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = output_path
    print(f"\n==================================================")
    print(f">>> Đang render: {cam_name} -> {output_path} (Ẩn mái: {hide_roofs})")
    print(f"==================================================")
    bpy.ops.render.render(write_still=True)
    print(f">>> Đã render xong: {output_path}")

# Khôi phục hiện mái và lưu lại file .blend hoàn thiện
for ro in roof_objs:
    ro.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath="d:/Work/Khu_Nha_Dong_Ho/khu_nha_dong_ho.blend")
print("\n>>> TẤT CẢ CÁC HÌNH ẢNH ĐÃ RENDER THÀNH CÔNG RỰC RỠ!")
