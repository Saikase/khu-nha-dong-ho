"""
KỊCH BẢN RENDER TOÀN BỘ 6 GÓC PHỐI CẢNH ĐỈNH CAO BẰNG BLENDER CYCLES
"""
import bpy

# Danh sách các mái ngói để ẩn/hiện khi bóc mái
roof_objs = [obj for obj in bpy.data.objects if "Mai" in obj.name or "MuNgoi" in obj.name or "KimNoc" in obj.name or "BoNoc" in obj.name or "HoLo" in obj.name or "CoDiem" in obj.name]

bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900

render_tasks = [
    # 1. Các phối cảnh chính khuôn viên & bóc mái nội thất
    ("Cam_1_TongThe", "d:/Work/Khu_Nha_Dong_Ho/blender_1_tong_the_co_mai.png", False),
    ("Cam_2_BocMai", "d:/Work/Khu_Nha_Dong_Ho/blender_2_boc_mai_noi_that.png", True),   # Ẩn toàn bộ mái để nhìn thấu 100% nội thất
    ("Cam_8_NoiThat_Nha3Gian", "d:/Work/Khu_Nha_Dong_Ho/blender_8_noithat_nha3gian.png", False), # Cận cảnh nội thất Nhà 3 Gian
    
    # 2. Bốn góc phối cảnh 4 hướng ĐÔNG - TÂY - NAM - BẮC
    ("Cam_Huong_Nam", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_nam.png", False),    # View từ hướng Nam (Cổng chính vào)
    ("Cam_Huong_Bac", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_bac.png", False),    # View từ hướng Bắc (Cuối đất nhìn về cổng)
    ("Cam_Huong_Dong", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_dong.png", False),  # View từ hướng Đông (Sườn phải sang trái)
    ("Cam_Huong_Tay", "d:/Work/Khu_Nha_Dong_Ho/blender_view_huong_tay.png", False),    # View từ hướng Tây (Sườn trái sang phải)

    # 3. Các phối cảnh cận cảnh chi tiết
    ("Cam_5_ViewAo_PhongNgam", "d:/Work/Khu_Nha_Dong_Ho/blender_5_view_ao_ca.png", False),
    ("Cam_7_HanhLang_NhaKhach", "d:/Work/Khu_Nha_Dong_Ho/blender_7_hanh_lang_nhakhach.png", False),
    ("Cam_3_DaiLucGiac_Nha3Gian", "d:/Work/Khu_Nha_Dong_Ho/blender_3_dai_luc_giac_nha3gian.png", False),
    ("Cam_4_KyVat_NhaAn", "d:/Work/Khu_Nha_Dong_Ho/blender_4_ky_vat_nha_an.png", False),
    ("Cam_6_CongChinh", "d:/Work/Khu_Nha_Dong_Ho/blender_6_cong_chinh.png", False),
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
print("\n>>> TẤT CẢ 6 HÌNH ẢNH ĐÃ RENDER THÀNH CÔNG RỰC RỠ!")
