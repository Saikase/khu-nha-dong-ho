"""
=============================================================================
MÔ HÌNH 3D SIÊU THỰC - KHU NHÀ DÒNG HỌ TRUYỀN THỐNG VIỆT NAM (18m x 37m)
BLENDER 4.2+ CYCLES ENGINE (NỘI THẤT NHÀ KHÁCH THỰC TẾ & AO CÁ VƯỜN QUÊ DÂN DÃ)
=============================================================================
"""

import bpy
import math

def clear_scene():
    """Xóa sạch scene cũ để tái tạo toàn bộ"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for c in list(bpy.data.cameras):
        bpy.data.cameras.remove(c)
    for l in list(bpy.data.lights):
        bpy.data.lights.remove(l)

def create_pbr_material(name, base_color, roughness=0.5, metallic=0.0, transmission=0.0, ior=1.45, emission_color=None, emission_strength=0.0):
    """Tạo vật liệu PBR Principled BSDF cao cấp"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
        if 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = ior
        if emission_color and 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

def add_box(name, location, size, material=None):
    """Tạo khối hộp chuẩn từ min coords (x, y, z)"""
    sx, sy, sz = size
    lx = location[0] + sx / 2.0
    ly = location[1] + sy / 2.0
    lz = location[2] + sz / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, ly, lz), scale=(sx, sy, sz))
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def add_cylinder(name, location, radius, height, material=None, vertices=32):
    """Tạo hình trụ đứng"""
    lx = location[0]
    ly = location[1]
    lz = location[2] + height / 2.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=height, location=(lx, ly, lz))
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    if material:
        obj.data.materials.append(material)
    return obj

def add_cone(name, location, radius1, height, material=None, vertices=32):
    """Tạo hình nón / chóp"""
    lx = location[0]
    ly = location[1]
    lz = location[2] + height / 2.0
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, depth=height, location=(lx, ly, lz))
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    if material:
        obj.data.materials.append(material)
    return obj

def add_sphere(name, location, radius, scale=(1.0, 1.0, 1.0), material=None):
    """Tạo hình cầu / đá cuội"""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=10, radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    if material:
        obj.data.materials.append(material)
def add_door_panel(name, hinge_pos, width, thickness, height, angle_deg, mat_panel=None, mat_handle=None):
    """Tạo cánh cửa gỗ mở góc angle_deg (độ) quanh bản lề hinge_pos (xh, yh, zh) kèm tay nắm gạt"""
    xh, yh, zh = hinge_pos
    rad = math.radians(angle_deg)
    cx = xh - math.sin(rad) * (width / 2.0)
    cy = yh + math.cos(rad) * (width / 2.0)
    cz = zh + height / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz), scale=(thickness, width, height))
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler[2] = rad
    if mat_panel:
        obj.data.materials.append(mat_panel)
    
    # Tay nắm cửa hợp kim cao cấp
    if mat_handle:
        hw = width - 0.08
        hx = xh - math.sin(rad) * hw
        hy = yh + math.cos(rad) * hw
        hz = zh + 1.0
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.015, depth=0.12, location=(hx, hy, hz))
        h_obj = bpy.context.active_object
        h_obj.name = f"{name}_TayNam"
        h_obj.rotation_euler[0] = math.radians(90)
        h_obj.data.materials.append(mat_handle)
    return obj

def add_gabled_roof(name, x_min, x_max, y_min, y_max, z_base, z_ridge, overhang=0.4, material=None):
    """Tạo mái dốc ngói truyền thống 2 mái chữ A"""
    x1 = x_min - overhang
    x2 = x_max + overhang
    y1 = y_min - overhang
    y2 = y_max + overhang
    xm = (x_min + x_max) / 2.0
    
    verts = [
        (x1, y1, z_base),
        (x2, y1, z_base),
        (x2, y2, z_base),
        (x1, y2, z_base),
        (xm, y1, z_ridge),
        (xm, y2, z_ridge)
    ]
    faces = [
        (0, 1, 4),
        (1, 2, 5, 4),
        (2, 3, 5),
        (3, 0, 4, 5),
        (0, 3, 2, 1)
    ]
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

def add_tree(name, location, trunk_r=0.2, height=3.5, foliage_r=1.5, wood_mat=None, leaf_mat=None):
    """Cây ăn trái bóng mát cổ truyền xum xuê"""
    lx, ly, lz = location
    add_cylinder(f"{name}_than", (lx, ly, lz), trunk_r, height * 0.45, wood_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=foliage_r, location=(lx, ly, lz + height * 0.75))
    fol = bpy.context.active_object
    fol.name = f"{name}_tan"
    bpy.ops.object.shade_smooth()
    if leaf_mat:
        fol.data.materials.append(leaf_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=foliage_r * 0.7, location=(lx + 0.15, ly - 0.1, lz + height * 0.95))
    fol2 = bpy.context.active_object
    fol2.name = f"{name}_tan2"
    bpy.ops.object.shade_smooth()
    if leaf_mat:
        fol2.data.materials.append(leaf_mat)

def add_chair(name, location, mat=None):
    """Ghế ăn gỗ lim chuẩn tỷ lệ"""
    lx, ly, lz = location
    for dx, dy in [(-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)]:
        add_cylinder(f"{name}_chan_{dx}_{dy}", (lx+dx, ly+dy, lz), 0.025, 0.45, mat)
    add_box(f"{name}_dem", (lx-0.22, ly-0.22, lz+0.43), (0.44, 0.44, 0.05), mat)
    add_box(f"{name}_tua", (lx-0.22, ly+0.18, lz+0.45), (0.44, 0.04, 0.45), mat)

def add_light_source(name, location, energy=20.0, color=(1.0, 0.90, 0.75), light_type='POINT'):
    """Thêm nguồn sáng điểm/khu vực ấm cúng cho nội thất"""
    bpy.ops.object.light_add(type=light_type, location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.color = color
    return light

# =============================================================================
# HÀM MÔ HÌNH HÓA ĐÀN CÁ AO QUÊ TRUYỀN THỐNG (CÁ CHÉP, CÁ ĐỒNG)
# =============================================================================
def add_carp_fish(name, location, yaw_deg=0.0, scale=0.75, mat_body=None, mat_fin=None):
    """Tạo chú cá chép đồng / cá ao quê tự nhiên, dân dã bơi lội dưới nước"""
    lx, ly, lz = location
    # 1. Thân cá chép dẹp 2 bên, vảy ánh bạc đồng tự nhiên
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.16, location=(lx, ly, lz))
    body = bpy.context.active_object
    body.name = f"{name}_body"
    body.scale = (scale * 0.50, scale * 2.4, scale * 0.85)
    body.rotation_euler = (0, 0, math.radians(yaw_deg))
    bpy.ops.object.shade_smooth()
    if mat_body:
        body.data.materials.append(mat_body)

    # 2. Vây lưng cá chép
    rad = math.radians(yaw_deg)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.04 * scale, depth=0.25 * scale, location=(lx, ly, lz + 0.12 * scale))
    dorsal = bpy.context.active_object
    dorsal.name = f"{name}_dorsal"
    dorsal.rotation_euler = (0, math.radians(20), rad)
    dorsal.scale = (0.1, 1.2, 0.8)
    bpy.ops.object.shade_smooth()
    if mat_fin:
        dorsal.data.materials.append(mat_fin)

    # 3. Đuôi cá chép chữ V chẻ đôi mềm mại
    rad_t = math.radians(yaw_deg)
    tx = lx - 0.42 * scale * math.sin(rad_t)
    ty = ly - 0.42 * scale * math.cos(rad_t)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.10 * scale, depth=0.32 * scale, location=(tx, ty, lz))
    tail = bpy.context.active_object
    tail.name = f"{name}_tail"
    tail.rotation_euler = (math.radians(90), 0, rad_t)
    tail.scale = (0.15, 1.0, 1.3)
    bpy.ops.object.shade_smooth()
    if mat_fin:
        tail.data.materials.append(mat_fin)

# =============================================================================
# HÀM MÔ HÌNH HÓA HOA SEN & HOA SÚNG AO LÀNG
# =============================================================================
def add_lotus_cluster(name, center, mat_leaf, mat_petal, mat_yellow):
    """Cụm hoa súng / sen ao làng truyền thống"""
    cx, cy, cz = center
    # 1. Các phiến lá tròn xanh dập dờn trên mặt nước
    leaf_offsets = [
        (0.0, 0.0, 0.42, 0.0),
        (0.48, -0.30, 0.35, 0.01),
        (-0.45, 0.35, 0.42, -0.01),
        (0.38, 0.46, 0.32, 0.01),
        (-0.52, -0.38, 0.36, 0.0)
    ]
    for idx, (ox, oy, r, dz) in enumerate(leaf_offsets):
        add_cylinder(f"{name}_la_{idx}", (cx + ox, cy + oy, cz + dz), r, 0.012, mat_leaf, vertices=24)

    # 2. Hoa sen hồng nở thanh tao
    fx, fy, fz = cx + 0.10, cy + 0.10, cz + 0.05
    add_cylinder(f"{name}_cuong", (fx, fy, cz - 0.25), 0.018, 0.32, mat_leaf)
    add_cylinder(f"{name}_nhuy", (fx, fy, fz + 0.02), 0.07, 0.04, mat_yellow)
    for ip in range(8):
        pang = math.radians(ip * 45)
        px = fx + 0.12 * math.cos(pang)
        py = fy + 0.12 * math.sin(pang)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.065, depth=0.15, location=(px, py, fz + 0.03))
        petal = bpy.context.active_object
        petal.name = f"{name}_canh_{ip}"
        petal.rotation_euler = (math.radians(35) * math.sin(pang), -math.radians(35) * math.cos(pang), pang)
        bpy.ops.object.shade_smooth()
        petal.data.materials.append(mat_petal)

    # 3. Búp sen vươn cao
    bx, by, bz = cx - 0.25, cy + 0.22, cz + 0.18
    add_cylinder(f"{name}_cuong_bup", (bx, by, cz - 0.25), 0.016, 0.45, mat_leaf)
    add_cone(f"{name}_bup", (bx, by, bz), 0.06, 0.16, mat_petal)


def build_compound():
    print(">>> [BLENDER] Khởi tạo mô hình Khu Nhà Dòng Họ - Nhà Khách & Ao Cá Vườn Quê...")
    clear_scene()

    # =========================================================================
    # 1. BẢNG MÀU & VẬT LIỆU CHUẨN KIẾN TRÚC TRUYỀN THỐNG VIỆT NAM
    # =========================================================================
    mat_roof_red    = create_pbr_material("Roof_NgoiDoBatTrang", (0.52, 0.13, 0.05, 1.0), roughness=0.65)
    mat_wood_dark   = create_pbr_material("Wood_GoLimLao",       (0.18, 0.08, 0.03, 1.0), roughness=0.32)
    mat_wood_warm   = create_pbr_material("Wood_GoHuong",        (0.48, 0.20, 0.07, 1.0), roughness=0.38)
    mat_wood_deck   = create_pbr_material("Wood_CauAoGoLim",     (0.28, 0.15, 0.06, 1.0), roughness=0.55)
    mat_wood_floor  = create_pbr_material("Wood_SanGoNoiThat",   (0.55, 0.32, 0.14, 1.0), roughness=0.35)
    mat_wall        = create_pbr_material("Wall_VoiNgaTrang",     (0.93, 0.92, 0.89, 1.0), roughness=0.70)
    mat_blue_stone  = create_pbr_material("Stone_DaXanhThanh",   (0.42, 0.48, 0.54, 1.0), roughness=0.48)
    mat_road_basalt = create_pbr_material("Stone_DaBazanDuong",  (0.20, 0.22, 0.24, 1.0), roughness=0.62)
    mat_paver_gray  = create_pbr_material("Stone_DaSanNoiBo",    (0.75, 0.73, 0.70, 1.0), roughness=0.65)
    mat_grass       = create_pbr_material("Nature_CoNhungXanh",   (0.18, 0.50, 0.12, 1.0), roughness=0.85)
    
    # Đáy ao làng đất cát tự nhiên
    mat_pond_bottom = create_pbr_material("Nature_DayAoDatCat",   (0.48, 0.52, 0.45, 1.0), roughness=0.65)
    mat_pond_wall   = create_pbr_material("Nature_BoAoDatKeDa",   (0.42, 0.45, 0.40, 1.0), roughness=0.60)
    
    # NƯỚC AO CÁ QUÊ: Màu xanh ngọc lục tự nhiên trong mát, phản chiếu bóng cây vườn và mây trời
    mat_water       = create_pbr_material("Nature_NuocAoQue",     (0.08, 0.55, 0.48, 1.0), roughness=0.04, transmission=0.88, ior=1.333)
    
    # Kính cường lực trong suốt lấy sáng
    mat_glass       = create_pbr_material("Arch_KinhCuongLuc",    (0.92, 0.97, 1.00, 1.0), roughness=0.02, transmission=0.96, ior=1.52)
    mat_gold        = create_pbr_material("Deco_ThepVang9999",    (0.95, 0.75, 0.10, 1.0), roughness=0.22, metallic=0.85)
    mat_pebble      = create_pbr_material("Stone_SoiCuoiTrang",   (0.92, 0.92, 0.88, 1.0), roughness=0.68)
    mat_rock_river  = create_pbr_material("Stone_DaCuoiBoAo",    (0.52, 0.50, 0.46, 1.0), roughness=0.55)
    mat_clay_mill   = create_pbr_material("Deco_DatNenCoiXay",    (0.45, 0.32, 0.20, 1.0), roughness=0.88)
    
    # Nội thất Nhà Khách
    mat_white_linen = create_pbr_material("Int_GaGiuongTrang",    (0.96, 0.96, 0.95, 1.0), roughness=0.75)
    mat_gold_runner = create_pbr_material("Int_ChanPhuVang",      (0.78, 0.52, 0.16, 1.0), roughness=0.55)
    mat_pillow      = create_pbr_material("Int_GoiNgu",           (0.92, 0.90, 0.85, 1.0), roughness=0.70)
    mat_ceramic_wc  = create_pbr_material("Int_SuTrangWC",        (0.98, 0.98, 0.98, 1.0), roughness=0.15)
    mat_slate_wc    = create_pbr_material("Int_DaSanWC",          (0.32, 0.34, 0.36, 1.0), roughness=0.45)
    mat_black_marble= create_pbr_material("Int_DaDenLavabo",      (0.10, 0.10, 0.12, 1.0), roughness=0.25)
    mat_chrome      = create_pbr_material("Int_KimLoaiCrom",      (0.85, 0.85, 0.88, 1.0), roughness=0.10, metallic=0.95)
    mat_cushion     = create_pbr_material("Int_DemNgoiVaiDui",    (0.72, 0.68, 0.58, 1.0), roughness=0.80)
    mat_tea_pot     = create_pbr_material("Int_AmTraGomMoc",      (0.42, 0.24, 0.14, 1.0), roughness=0.45)
    mat_rug         = create_pbr_material("Int_ThamPhongKhach",   (0.82, 0.76, 0.68, 1.0), roughness=0.90)
    mat_wood_door   = create_pbr_material("Wood_CuaPhongNgu",     (0.35, 0.16, 0.06, 1.0), roughness=0.35)
    mat_brass       = create_pbr_material("Metal_TayNamCua",      (0.92, 0.72, 0.15, 1.0), roughness=0.20, metallic=0.90)
    
    # Vật liệu cổ truyền Nhà 3 Gian Bắc Bộ
    mat_lacquer_red     = create_pbr_material("Deco_SonSonDo",        (0.75, 0.08, 0.05, 1.0), roughness=0.25)
    mat_terracotta_floor= create_pbr_material("Floor_GachBatTrang",   (0.58, 0.22, 0.10, 1.0), roughness=0.55)
    mat_mat_rush        = create_pbr_material("Int_ChieuCoiHoa",      (0.85, 0.78, 0.58, 1.0), roughness=0.85)
    mat_cushion_red     = create_pbr_material("Int_GoiGamDo",         (0.80, 0.10, 0.12, 1.0), roughness=0.45)
    mat_bronze          = create_pbr_material("Metal_DongHunCo",      (0.35, 0.28, 0.18, 1.0), roughness=0.30, metallic=0.75)
    
    # CÁ AO BÌNH THƯỜNG (Cá chép đồng, cá chép đỏ quê, cá trôi bạc)
    mat_carp_silver = create_pbr_material("Ca_ChepDongBac", (0.55, 0.58, 0.56, 1.0), roughness=0.25, metallic=0.35, emission_color=(0.60, 0.65, 0.60, 1.0), emission_strength=0.3)
    mat_carp_gold   = create_pbr_material("Ca_ChepVangDong", (0.75, 0.55, 0.20, 1.0), roughness=0.25, metallic=0.30, emission_color=(0.80, 0.58, 0.20, 1.0), emission_strength=0.35)
    mat_carp_red    = create_pbr_material("Ca_ChepDoQue",   (0.88, 0.28, 0.08, 1.0), roughness=0.25, emission_color=(0.90, 0.30, 0.08, 1.0), emission_strength=0.4)
    mat_carp_fin    = create_pbr_material("Ca_VayCa",       (0.70, 0.40, 0.18, 1.0), roughness=0.30, emission_color=(0.70, 0.40, 0.18, 1.0), emission_strength=0.2)
    
    mat_lotus_leaf  = create_pbr_material("Lotus_LaSen",    (0.08, 0.42, 0.12, 1.0), roughness=0.40)
    mat_lotus_pink  = create_pbr_material("Lotus_CanhSen",  (0.95, 0.38, 0.55, 1.0), roughness=0.30, emission_color=(0.95, 0.38, 0.55, 1.0), emission_strength=0.15)
    mat_lotus_yellow= create_pbr_material("Lotus_NhuyVang", (0.98, 0.85, 0.08, 1.0), roughness=0.25, emission_color=(0.98, 0.85, 0.08, 1.0), emission_strength=0.25)

    # =========================================================================
    # 2. ĐẤT NỀN BỐI CẢNH NGOÀI RANH ĐẤT (KHÔNG CẮT QUA LÒNG AO!)
    # =========================================================================
    add_box("Co_Ngoai_Nam", (-10.0, -10.0, -0.2), (38.0, 10.0, 0.2), mat_grass)
    add_box("Co_Ngoai_Bac", (-10.0, 37.0, -0.2),  (38.0, 10.0, 0.2), mat_grass)
    add_box("Co_Ngoai_Tay", (-10.0, 0.0, -0.2),   (10.0, 37.0, 0.2), mat_grass)
    add_box("Co_Ngoai_Dong", (18.0, 0.0, -0.2),   (10.0, 37.0, 0.2), mat_grass)

    # =========================================================================
    # 3. TRỤC ĐƯỜNG CHÍNH 4.0m XUYÊN SUỐT 37.0m (X = 7 -> 11)
    # =========================================================================
    add_box("DuongChinh_4m", (7.0, 0.0, 0.01), (4.0, 37.0, 0.03), mat_road_basalt)
    add_box("BoVia_Trai_4m", (6.88, 0.0, 0.0), (0.12, 37.0, 0.06), mat_blue_stone)
    add_box("BoVia_Phai_4m", (11.0, 0.0, 0.0), (0.12, 37.0, 0.06), mat_blue_stone)

    # Cột đèn đá dẫn lối phong cách cổ truyền
    for yd in range(3, 36, 6):
        add_cylinder(f"DenDa_Phai_{yd}", (11.2, yd, 0.0), 0.10, 1.1, mat_blue_stone)
        add_box(f"LongDen_Phai_{yd}", (11.12, yd-0.08, 1.05), (0.16, 0.16, 0.22), mat_gold)
        add_cylinder(f"DenDa_Trai_{yd}", (6.8, yd, 0.0), 0.10, 1.1, mat_blue_stone)
        add_box(f"LongDen_Trai_{yd}", (6.72, yd-0.08, 1.05), (0.16, 0.16, 0.22), mat_gold)

    # =========================================================================
    # 4. TƯỜNG RÀO RANH ĐẤT & CỔNG TAM QUAN TRUYỀN THỐNG
    # =========================================================================
    hw = 2.4  # chiều cao tường bao
    tw = 0.22 # độ dày tường
    add_box("TuongRao_Trai", (-tw, 0.0, 0.0), (tw, 37.0, hw), mat_wall)
    add_box("TuongRao_Phai", (18.0, 0.0, 0.0), (tw, 37.0, hw), mat_wall)
    add_box("TuongRao_Sau",  (-tw, 37.0, 0.0), (18.0 + 2*tw, tw, hw), mat_wall)
    add_box("TuongRao_Tien_Trai", (-tw, -tw, 0.0), (7.0 + tw, tw, hw), mat_wall)
    add_box("TuongRao_Tien_Phai", (11.0, -tw, 0.0), (7.0 + tw, tw, hw), mat_wall)

    # Mũ ngói đỏ trên tường bao
    add_box("MuNgoi_Trai", (-tw - 0.06, -tw, hw), (tw + 0.12, 37.0 + tw, 0.08), mat_roof_red)
    add_box("MuNgoi_Phai", (18.0 - 0.06, -tw, hw), (tw + 0.12, 37.0 + tw, 0.08), mat_roof_red)
    add_box("MuNgoi_Sau",  (-tw, 37.0 - 0.06, hw), (18.0 + 2*tw, tw + 0.12, 0.08), mat_roof_red)
    add_box("MuNgoi_Tien_Trai", (-tw, -tw - 0.06, hw), (7.0 + tw, tw + 0.12, 0.08), mat_roof_red)
    add_box("MuNgoi_Tien_Phai", (11.0, -tw - 0.06, hw), (7.0 + tw, tw + 0.12, 0.08), mat_roof_red)

    # Cổng Tam Quan: Trụ biểu đá xanh cao 4.2m
    add_box("TruCong_Trai", (6.65, -0.45, 0.0), (0.65, 0.65, 4.2), mat_blue_stone)
    add_box("TruCong_Phai", (10.7, -0.45, 0.0), (0.65, 0.65, 4.2), mat_blue_stone)
    add_cone("BupSen_Cong_Trai", (6.97, -0.12, 4.2), 0.28, 0.55, mat_blue_stone)
    add_cone("BupSen_Cong_Phai", (11.02, -0.12, 4.2), 0.28, 0.55, mat_blue_stone)
    add_box("XaNgang_Cong", (6.95, -0.3, 3.4), (4.1, 0.35, 0.45), mat_wood_dark)
    add_box("HoanhPhi_Cong", (7.8, -0.36, 3.45), (2.4, 0.06, 0.35), mat_gold)
    add_gabled_roof("Mai_CongChinh", 6.8, 11.2, -0.65, 0.15, 3.85, 4.5, overhang=0.3, material=mat_roof_red)
    add_box("CanhCong_Trai", (7.0, 0.0, 0.0), (0.08, 1.6, 3.2), mat_wood_dark)
    add_box("CanhCong_Phai", (10.92, 0.0, 0.0), (0.08, 1.6, 3.2), mat_wood_dark)

    # =========================================================================
    # 5. DÃY BÊN PHẢI (X = 11.0 -> 18.0, Dài 37.0m)
    # =========================================================================
    add_box("DaiLui_Phai_1m", (17.0, 0.0, 0.005), (1.0, 37.0, 0.02), mat_paver_gray)

    # --- KHU 3: CỤM BẾP, 2 WC, NHÀ ĂN & HÀNH LANG KỶ VẬT (Y = 0 -> 13.5) ---
    add_box("WC_Khu3_Tuong", (16.5, 0.0, 0.0), (1.5, 3.0, 2.8), mat_wall)
    add_box("WC_VachNgan",   (16.5, 1.5, 0.0), (1.5, 0.12, 2.8), mat_wall)
    add_box("WC_Cua1", (16.48, 0.35, 0.0), (0.05, 0.75, 2.1), mat_wood_dark)
    add_box("WC_Cua2", (16.48, 1.85, 0.0), (0.05, 0.75, 2.1), mat_wood_dark)

    add_box("Bep_TuongBao", (11.0, 0.0, 0.0), (5.5, 3.0, 3.2), mat_wall)
    add_box("Bep_BanL1", (11.2, 0.2, 0.0), (0.7, 2.6, 0.85), mat_blue_stone)
    add_box("Bep_BanL2", (11.9, 0.2, 0.0), (3.5, 0.7, 0.85), mat_blue_stone)
    add_gabled_roof("Mai_Bep_WC", 10.8, 18.0, 0.0, 3.0, 3.2, 4.1, overhang=0.4, material=mat_roof_red)

    # Nhà Ăn Gia Tộc Rộng Rãi (63m²)
    add_box("NhaAn_Nen", (11.0, 3.0, 0.02), (6.0, 10.5, 0.08), mat_paver_gray)
    add_box("NhaAn_TuongDau", (11.0, 3.0, 0.0), (6.0, 0.2, 3.5), mat_wall)
    add_box("NhaAn_TuongCuoi", (11.0, 13.3, 0.0), (6.0, 0.2, 3.5), mat_wall)
    for yp in [3.0, 5.6, 8.25, 10.8, 13.3]:
        add_cylinder(f"Cot_NhaAn_{yp}", (11.15, yp, 0.0), 0.14, 3.5, mat_wood_dark)
    add_box("Kinh_NhaAn_Duong4m", (11.2, 3.2, 0.0), (0.04, 10.0, 3.4), mat_glass)
    add_box("Kinh_NhaAn_ViewKyVat", (16.96, 3.2, 0.0), (0.04, 10.0, 3.4), mat_glass)
    add_gabled_roof("Mai_NhaAn", 10.8, 17.2, 3.0, 13.5, 3.5, 4.6, overhang=0.4, material=mat_roof_red)

    add_light_source("Den_NhaAn_1", (14.0, 6.5, 2.8), energy=45.0, color=(1.0, 0.92, 0.80))
    add_light_source("Den_NhaAn_2", (14.0, 10.0, 2.8), energy=45.0, color=(1.0, 0.92, 0.80))

    # Bàn Ăn Thông Minh Gia Tộc
    add_box("BanAn_ThongMinh_Than", (12.8, 5.8, 0.0), (2.4, 4.9, 0.72), mat_wood_warm)
    add_box("BanAn_ThongMinh_Mat",  (12.7, 5.6, 0.72), (2.6, 5.3, 0.06), mat_wood_dark)
    for ig in range(5):
        add_chair(f"GheAn_Trai_{ig}", (12.2, 6.0 + ig*1.0, 0.0), mat_wood_dark)
        add_chair(f"GheAn_Phai_{ig}", (15.8, 6.0 + ig*1.0, 0.0), mat_wood_dark)
    add_chair("GheAn_Dau1", (14.0, 5.0, 0.0), mat_wood_dark)
    add_chair("GheAn_Dau2", (14.0, 11.4, 0.0), mat_wood_dark)

    # Dải kỷ vật xưa
    add_box("NenSoi_KyVat", (17.02, 3.0, 0.02), (0.96, 10.5, 0.04), mat_pebble)
    for yst in [4.2, 5.8, 7.5, 9.2, 11.0, 12.6]:
        add_cylinder(f"DaBuoc_KyVat_{yst}", (17.5, yst, 0.04), 0.22, 0.03, mat_blue_stone)

    add_light_source("Spot_CoiXay", (17.5, 6.2, 2.5), energy=60.0, color=(1.0, 0.88, 0.70))
    add_light_source("Spot_CoiGia", (17.5, 9.8, 2.5), energy=60.0, color=(1.0, 0.88, 0.70))

    # 1. Cối xay thóc nan tre
    add_cylinder("CoiXay_ThotDuoi", (17.5, 6.2, 0.06), 0.42, 0.45, mat_clay_mill)
    add_cylinder("CoiXay_VanhTre",  (17.5, 6.2, 0.06), 0.44, 0.42, mat_wood_warm)
    add_box("CoiXay_MangChay", (17.08, 6.05, 0.15), (0.18, 0.3, 0.1), mat_wood_dark)
    add_cylinder("CoiXay_ThotTren", (17.5, 6.2, 0.51), 0.38, 0.38, mat_clay_mill)
    add_cylinder("CoiXay_NgongCoi", (17.5, 6.2, 0.89), 0.04, 0.25, mat_wood_dark)
    add_box("CoiXay_CanGiang", (17.15, 6.16, 1.10), (0.7, 0.08, 0.08), mat_wood_dark)

    # Rặng trúc quân tử
    for ytr in [7.7, 8.1, 8.5, 8.9]:
        add_cylinder(f"TrucCanh_{ytr}", (17.75, ytr, 0.0), 0.03, 2.6, mat_grass)
        add_cone(f"LaTruc_{ytr}", (17.75, ytr, 2.0), 0.35, 1.0, mat_grass)

    # 2. Cối giã gạo cần đạp chân
    add_cylinder("CoiGia_CoiDa", (17.5, 9.6, 0.06), 0.36, 0.46, mat_blue_stone)
    add_cylinder("CoiGia_LongCoi", (17.5, 9.6, 0.45), 0.24, 0.10, mat_clay_mill)
    add_box("CoiGia_TruDo", (17.35, 10.5, 0.0), (0.3, 0.14, 0.55), mat_wood_dark)
    add_box("CoiGia_CanDap", (17.44, 9.5, 0.42), (0.12, 2.2, 0.12), mat_wood_dark)
    add_cylinder("CoiGia_Chay", (17.5, 9.6, 0.15), 0.07, 0.35, mat_wood_dark)

    # --- KHU 2: ĐÀI LỤC GIÁC 6.0M & 2 SÂN THOÁNG (Y = 13.5 -> 25.5, 12.0m) ---
    add_box("San_Khu2_Tong", (11.0, 13.5, 0.005), (6.0, 12.0, 0.025), mat_paver_gray)
    xc, yc = 14.0, 19.5
    add_cylinder("De_DaiLucGiac_Cap1", (xc, yc, 0.0), 3.05, 0.20, mat_blue_stone, vertices=6)
    add_cylinder("De_DaiLucGiac_Cap2", (xc, yc, 0.20), 2.90, 0.20, mat_blue_stone, vertices=6)
    add_cylinder("San_Go_DaiLucGiac",  (xc, yc, 0.40), 2.80, 0.06, mat_wood_dark, vertices=6)

    r_col = 2.6
    for ic in range(6):
        ang = math.radians(ic * 60 + 30)
        px = xc + r_col * math.cos(ang)
        py = yc + r_col * math.sin(ang)
        add_cylinder(f"ChanDe_CotChoi_{ic}", (px, py, 0.40), 0.18, 0.15, mat_blue_stone)
        add_cylinder(f"CotChoi_LucGiac_{ic}", (px, py, 0.55), 0.13, 2.85, mat_wood_dark)
        if ic != 1:
            ang_next = math.radians((ic+1) * 60 + 30)
            mx = xc + (r_col - 0.1) * math.cos((ang + ang_next)/2.0)
            my = yc + (r_col - 0.1) * math.sin((ang + ang_next)/2.0)
            add_cylinder(f"LanCan_Choi_{ic}", (mx, my, 0.46), 0.06, 0.65, mat_wood_warm)

    add_cylinder("BanTra_DaiLucGiac", (xc, yc, 0.46), 0.75, 0.75, mat_wood_dark, vertices=6)
    for idn in range(6):
        d_ang = math.radians(idn * 60)
        dx = xc + 1.4 * math.cos(d_ang)
        dy = yc + 1.4 * math.sin(d_ang)
        add_cylinder(f"DonGhe_LucGiac_{idn}", (dx, dy, 0.46), 0.22, 0.45, mat_wood_warm)

    add_cone("MaiChoi_Tang1", (xc, yc, 3.4), 3.55, 1.15, mat_roof_red, vertices=6)
    add_cylinder("CoDiem_ThongGio", (xc, yc, 4.35), 1.75, 0.45, mat_wood_dark, vertices=6)
    add_cone("MaiChoi_Tang2", (xc, yc, 4.8), 2.15, 1.35, mat_roof_red, vertices=6)
    add_cylinder("HoLo_De", (xc, yc, 6.15), 0.20, 0.15, mat_gold)
    add_cone("HoLo_Dinh", (xc, yc, 6.30), 0.16, 0.50, mat_gold)

    # --- KHU 1: NHÀ 3 GIAN BẮC BỘ TRUYỀN THỐNG (Y = 25.5 -> 37.0, Dài 11.5m) ---
    # Nội thất chuẩn mực cổ truyền: Gian giữa thờ tổ tiên thếp vàng, cửa võng,
    # hoành phi câu đối, lư hương hạc chầu; Gian tả tiếp khách trường kỷ, tủ chè
    # khảm ốc xà cừ; Gian hữu sập gụ đại chạm ngũ phúc, bàn cờ trà & tủ gia phả dòng họ.
    # -------------------------------------------------------------------------
    # Bậc tam cấp đá xanh và hiên hè
    add_box("TamCap_Nha3Gian", (10.5, 27.0, 0.0), (0.5, 6.0, 0.22), mat_blue_stone)
    add_box("He_Nha3Gian",     (11.0, 25.5, 0.0), (1.0, 9.0, 0.45), mat_blue_stone)
    add_box("San_Nha3Gian",    (12.0, 25.5, 0.0), (4.8, 9.0, 0.45), mat_paver_gray)
    add_box("San_GachBatTrang", (12.02, 25.52, 0.45), (4.74, 8.94, 0.02), mat_terracotta_floor)

    # Hàng 4 cột hiên tròn gỗ lim trên chân tảng đá xanh chạm cánh sen
    for yh in [25.8, 28.8, 31.8, 34.2]:
        add_cylinder(f"ChanTang_Hien_{yh}", (11.5, yh, 0.45), 0.18, 0.15, mat_blue_stone)
        add_cylinder(f"CotHien_Nha3Gian_{yh}", (11.5, yh, 0.60), 0.13, 2.85, mat_wood_dark)
    # Xà hiên nối hàng cột hiên
    add_box("XaHien_Nha3Gian", (11.45, 25.5, 3.35), (0.12, 9.0, 0.15), mat_wood_dark)

    # Tường hồi Nam (trái), tường hồi Bắc (phải) và tường hậu
    add_box("TuongHoi_Nam_Nha3Gian", (12.0, 25.5, 0.0), (5.0, 0.22, 3.6), mat_wall)
    add_box("TuongHoi_Bac_Nha3Gian", (12.0, 34.28, 0.0), (5.0, 0.22, 3.6), mat_wall)
    add_box("TuongHau_Nha3Gian",     (16.78, 25.5, 0.0), (0.22, 9.0, 3.6), mat_wall)

    # Vách mặt tiền gỗ lim và hệ cửa bức bàn 3 gian (tại X = 12.0)
    add_box("NguongCua_Nha3Gian",    (11.96, 25.5, 0.45), (0.10, 9.0, 0.12), mat_wood_dark)
    add_box("KhungCua_Dinh_Nha3Gian", (11.96, 25.5, 3.10), (0.10, 9.0, 0.12), mat_wood_dark)

    # 1. Cửa bức bàn Gian Tả (Y = 25.8 -> 28.2) - 2 cánh giữa mở hé 45 độ đón khách
    add_box("CuaBucBan_Ta_KhungL", (11.98, 25.80, 0.57), (0.05, 0.35, 2.53), mat_wood_dark)
    add_box("CuaBucBan_Ta_KhungR", (11.98, 27.85, 0.57), (0.05, 0.35, 2.53), mat_wood_dark)
    add_door_panel("CanhCua_Ta_1", (12.00, 26.15, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=45.0, mat_panel=mat_wood_dark)
    add_door_panel("CanhCua_Ta_2", (12.00, 27.85, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=-45.0, mat_panel=mat_wood_dark)

    # 2. Cửa bức bàn Gian Giữa (Y = 28.8 -> 31.2) - Mở rộng thênh thang nhìn thấu ban thờ tổ!
    add_box("CuaBucBan_Giua_KhungL", (11.98, 28.80, 0.57), (0.05, 0.35, 2.53), mat_wood_dark)
    add_box("CuaBucBan_Giua_KhungR", (11.98, 30.85, 0.57), (0.05, 0.35, 2.53), mat_wood_dark)
    add_door_panel("CanhCua_Giua_1", (12.00, 29.15, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=65.0, mat_panel=mat_wood_dark)
    add_door_panel("CanhCua_Giua_2", (12.00, 30.85, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=-65.0, mat_panel=mat_wood_dark)

    # 3. Cửa bức bàn Gian Hữu (Y = 31.8 -> 34.2) - 2 cánh giữa mở hé 45 độ
    add_box("CuaBucBan_Huu_KhungL", (11.98, 31.80, 0.57), (0.05, 0.35, 2.53), mat_wood_dark)
    add_box("CuaBucBan_Huu_KhungR", (11.98, 33.85, 0.57), (0.05, 0.35, 2.53), mat_wood_dark)
    add_door_panel("CanhCua_Huu_1", (12.00, 32.15, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=45.0, mat_panel=mat_wood_dark)
    add_door_panel("CanhCua_Huu_2", (12.00, 33.85, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=-45.0, mat_panel=mat_wood_dark)

    # Vách tiền phía trên cửa (ẩn khi bóc mái để nhìn thấu từ trên cao)
    add_box("Mai_VachTien_Nha3Gian", (11.96, 25.5, 3.22), (0.10, 9.0, 0.38), mat_wall)

    # Hệ thống vì kèo & cột cái, cột hậu, cột tiền bên trong nhà
    for yc in [28.5, 31.5]:
        add_cylinder(f"ChanTang_CotCai_{yc}", (14.0, yc, 0.47), 0.20, 0.15, mat_blue_stone)
        add_cylinder(f"CotCai_Nha3Gian_{yc}", (14.0, yc, 0.62), 0.15, 3.65, mat_wood_dark)
        add_cylinder(f"ChanTang_CotHau_{yc}", (16.4, yc, 0.47), 0.16, 0.15, mat_blue_stone)
        add_cylinder(f"CotHau_Nha3Gian_{yc}", (16.4, yc, 0.62), 0.12, 3.00, mat_wood_dark)
        add_cylinder(f"ChanTang_CotTien_{yc}",(12.2, yc, 0.47), 0.16, 0.15, mat_blue_stone)
        add_cylinder(f"CotTien_Nha3Gian_{yc}",(12.2, yc, 0.62), 0.12, 3.00, mat_wood_dark)
        add_box(f"XaLong_Tien_{yc}", (12.2, yc - 0.06, 3.10), (1.8, 0.12, 0.16), mat_wood_dark)
        add_box(f"XaLong_Hau_{yc}",  (14.0, yc - 0.06, 3.10), (2.4, 0.12, 0.16), mat_wood_dark)

    # Câu đầu nối 2 cột cái gian giữa
    add_box("CauDau_GianGiua", (13.92, 28.5, 3.45), (0.16, 3.0, 0.20), mat_wood_dark)

    # =========================================================================
    # GIAN GIỮA: NƠI THỜ TỔ TIÊN TRANG NGHIÊM (Y = 28.5 -> 31.5)
    # =========================================================================
    # 1. Bàn Thờ Đại An Gian (Hương án chính sơn son thếp vàng 2 cấp)
    add_box("AnGian_ChanDe",   (15.20, 29.10, 0.47), (1.50, 1.80, 0.25), mat_wood_dark)
    add_box("AnGian_DaTien",   (15.18, 29.08, 0.72), (1.54, 1.84, 0.45), mat_lacquer_red)
    add_box("AnGian_ChamRong", (15.16, 29.15, 0.75), (0.04, 1.70, 0.40), mat_gold)
    add_box("AnGian_MatBan",   (15.10, 29.00, 1.68), (1.65, 2.00, 0.06), mat_wood_dark)

    # Cấp 2 (Ngai thờ tam sơn phía sau): X = 16.1 -> 16.7, Y = 29.4 -> 30.6
    add_box("AnGian_Cap2_Than", (16.10, 29.40, 1.74), (0.60, 1.20, 0.35), mat_lacquer_red)
    add_box("AnGian_Cap2_Mat",  (16.05, 29.35, 2.09), (0.68, 1.30, 0.04), mat_gold)

    # Ngai Thờ Tổ Tiên & Bài Vị Sơn Son Thếp Vàng
    add_box("NgaiTho_De",   (16.25, 29.75, 2.13), (0.42, 0.50, 0.15), mat_gold)
    add_box("NgaiTho_TayL", (16.25, 29.70, 2.28), (0.42, 0.06, 0.35), mat_gold)
    add_box("NgaiTho_TayR", (16.25, 30.24, 2.28), (0.42, 0.06, 0.35), mat_gold)
    add_box("NgaiTho_Lung", (16.60, 29.72, 2.28), (0.06, 0.56, 0.52), mat_gold)
    add_box("BaiVi_ToTien", (16.45, 29.90, 2.28), (0.04, 0.20, 0.42), mat_gold)

    # 2. Bộ Ngũ Sự Đồ Thờ Bằng Đồng Hun & Vàng
    add_cylinder("LuDong_De",  (15.70, 30.00, 1.74), 0.15, 0.10, mat_bronze)
    add_cylinder("LuDong_Than",(15.70, 30.00, 1.84), 0.18, 0.25, mat_gold)
    add_cone("LuDong_Nap",     (15.70, 30.00, 2.09), 0.17, 0.15, mat_bronze)
    add_cylinder("LuDong_Nghe",(15.70, 30.00, 2.24), 0.06, 0.10, mat_gold)

    # Đôi Hạc Đồng ngự lưng Rùa đứng chầu 2 bên
    add_cylinder("Rua_Trai", (15.70, 29.62, 1.74), 0.11, 0.07, mat_bronze)
    add_cylinder("Hac_Trai", (15.70, 29.62, 1.81), 0.02, 0.40, mat_gold)
    add_cone("Hac_Canh_Trai",(15.70, 29.62, 2.21), 0.08, 0.18, mat_gold)

    add_cylinder("Rua_Phai", (15.70, 30.38, 1.74), 0.11, 0.07, mat_bronze)
    add_cylinder("Hac_Phai", (15.70, 30.38, 1.81), 0.02, 0.40, mat_gold)
    add_cone("Hac_Canh_Phai",(15.70, 30.38, 2.21), 0.08, 0.18, mat_gold)

    # Đôi chân nến đồng đỉnh thờ
    add_cylinder("ChanNen_Trai", (15.38, 29.35, 1.74), 0.07, 0.38, mat_bronze)
    add_cylinder("NenDo_Trai",   (15.38, 29.35, 2.12), 0.02, 0.15, mat_lacquer_red)
    add_cylinder("ChanNen_Phai", (15.38, 30.65, 1.74), 0.07, 0.38, mat_bronze)
    add_cylinder("NenDo_Phai",   (15.38, 30.65, 2.12), 0.02, 0.15, mat_lacquer_red)

    # Bát hương gốm men lam Bát Tràng ở phía trước
    add_cylinder("BatHuong_Lam", (15.36, 30.00, 1.74), 0.12, 0.18, mat_tea_pot)
    add_box("DaiNuoc_3Chen",     (15.22, 29.90, 1.74), (0.08, 0.20, 0.04), mat_gold)
    add_cylinder("MamBong_NguQua",(15.36, 30.70, 1.74), 0.14, 0.12, mat_gold)
    add_cylinder("OngHuong_Dong", (15.36, 29.20, 1.74), 0.06, 0.24, mat_bronze)

    # 3. Cửa Võng (Thiều Châu) chạm lộng rồng phụng thếp vàng buông rủ
    add_box("CuaVong_Dinh",  (14.00, 28.50, 3.25), (0.08, 3.00, 0.25), mat_gold)
    add_box("CuaVong_CanhL", (14.00, 28.50, 2.45), (0.08, 0.35, 0.80), mat_gold)
    add_box("CuaVong_CanhR", (14.00, 31.15, 2.45), (0.08, 0.35, 0.80), mat_gold)

    # 4. Bức Hoành Phi (Đại Tự) "ĐỨC LƯU QUANG" (德流光)
    add_box("HoanhPhi_Khung", (16.74, 29.10, 2.85), (0.04, 1.80, 0.65), mat_lacquer_red)
    add_box("HoanhPhi_Vang",  (16.73, 29.25, 2.95), (0.02, 1.50, 0.45), mat_gold)

    # 5. Đôi Câu Đối Lòng Máng Thếp Vàng ốp trên 2 cột cái
    add_box("CauDoi_CotTrai", (13.98, 28.46, 1.15), (0.06, 0.16, 2.20), mat_lacquer_red)
    add_box("CauDoi_CotPhai", (13.98, 31.46, 1.15), (0.06, 0.16, 2.20), mat_lacquer_red)

    # 6. Đôi Lục Bình Khổng Tước Gỗ Lim Đặt Uy Nghiêm 2 Bên
    for ylb, nlb in [(28.75, "Trai"), (31.25, "Phai")]:
        add_cylinder(f"LucBinh_{nlb}_De",   (15.90, ylb, 0.47), 0.18, 0.20, mat_wood_dark)
        add_cylinder(f"LucBinh_{nlb}_Than", (15.90, ylb, 0.67), 0.22, 0.85, mat_wood_dark)
        add_cone(f"LucBinh_{nlb}_Co",       (15.90, ylb, 1.52), 0.12, 0.35, mat_wood_dark)
        add_cone(f"LucBinh_{nlb}_Mieng",   (15.90, ylb, 1.87), 0.20, 0.12, mat_wood_dark)

    # 7. Bàn Tiền Dâng Lễ (Đặt phía trước án gian)
    add_box("BanTien_Le", (14.50, 29.40, 0.47), (0.55, 1.20, 0.80), mat_wood_dark)

    # 8. Chiếu Cói Hoa Đỏ Dệt Truyền Thống (Chiếu Ngự tế tổ)
    add_box("ChieuCoi_GianGiua", (12.50, 29.00, 0.47), (1.80, 2.00, 0.015), mat_mat_rush)

    # =========================================================================
    # GIAN TẢ: KHÔNG GIAN TIẾP KHÁCH TRƯỜNG KỶ & TỦ CHÈ (Y = 25.5 -> 28.5)
    # =========================================================================
    # 1. Bộ Bàn Ghế Trường Kỷ Gỗ Gụ Khắc Hạt Cườm
    add_box("TruongKy_Ghe1", (12.80, 26.00, 0.47), (0.65, 1.90, 0.42), mat_wood_dark)
    add_box("TruongKy_Tua1", (12.80, 26.00, 0.89), (0.12, 1.90, 0.42), mat_wood_dark)
    add_box("TruongKy_Ghe2", (14.50, 26.00, 0.47), (0.65, 1.90, 0.42), mat_wood_dark)
    add_box("TruongKy_Tua2", (15.03, 26.00, 0.89), (0.12, 1.90, 0.42), mat_wood_dark)
    add_box("TruongKy_Ban",  (13.70, 26.00, 0.47), (0.58, 1.90, 0.72), mat_wood_dark)
    add_box("TruongKy_Don",  (13.70, 28.15, 0.47), (0.50, 0.40, 0.68), mat_wood_dark)

    # Bộ ấm chén Bát Tràng men rạn & Điếu bát bọc đồng trên bàn trường kỷ
    add_box("KhayTra_TruongKy",   (13.80, 26.60, 1.19), (0.38, 0.60, 0.03), mat_wood_dark)
    add_cylinder("AmTra_TruongKy", (13.99, 26.80, 1.22), 0.06, 0.09, mat_tea_pot)
    add_cylinder("DieuBat_Dong",   (13.99, 27.50, 1.19), 0.09, 0.12, mat_bronze)

    # 2. Tủ Chè Cổ Gỗ Gụ Khảm Ốc Xà Cừ (Kê sát tường hậu)
    add_box("TuChe_Than",   (16.05, 26.00, 0.47), (0.68, 1.90, 0.88), mat_wood_dark)
    add_box("TuChe_KhamOc", (16.03, 26.15, 0.65), (0.02, 1.60, 0.60), mat_gold)
    add_cylinder("TuChe_LoHoa", (16.35, 26.40, 1.35), 0.08, 0.28, mat_tea_pot)
    add_box("TuChe_TamDa",      (16.35, 27.20, 1.35), (0.15, 0.45, 0.22), mat_gold)

    # 3. Tranh Tứ Bình Cổ (Tùng - Cúc - Trúc - Mai) trên tường hồi Nam
    for itb, xtb in enumerate([13.0, 13.8, 14.6, 15.4]):
        add_box(f"TranhTuBinh_{itb}", (xtb, 25.72, 1.65), (0.55, 0.02, 1.10), mat_wood_dark)

    # =========================================================================
    # GIAN HỮU: SẬP GỤ ĐẠI BA THÀNH & TỦ GIA PHẢ DÒNG HỌ (Y = 31.5 -> 34.5)
    # =========================================================================
    # 1. Sập Gụ Đại Ba Thành Gỗ Mun Chạm Ngũ Phúc (1.6m x 2.0m)
    add_box("SapGu_ChanDe", (12.80, 32.00, 0.47), (1.60, 2.00, 0.28), mat_wood_dark)
    add_box("SapGu_DaTien", (12.78, 31.98, 0.75), (1.64, 2.04, 0.20), mat_wood_dark)
    add_box("SapGu_MatSap", (12.75, 31.95, 0.95), (1.70, 2.10, 0.08), mat_wood_warm)
    add_box("SapGu_ThanhHau", (14.35, 31.95, 1.03), (0.10, 2.10, 0.35), mat_wood_dark)
    add_box("SapGu_ThanhTrai",(12.75, 31.95, 1.03), (1.60, 0.10, 0.35), mat_wood_dark)
    add_box("SapGu_ThanhPhai",(12.75, 33.95, 1.03), (1.60, 0.10, 0.35), mat_wood_dark)

    add_box("SapGu_BanTra", (13.35, 32.70, 1.03), (0.50, 0.60, 0.22), mat_wood_dark)
    add_cylinder("SapGu_AmTra", (13.60, 33.00, 1.25), 0.05, 0.08, mat_tea_pot)
    add_box("SapGu_Goi1", (12.95, 32.15, 1.03), (0.45, 0.22, 0.25), mat_cushion_red)
    add_box("SapGu_Goi2", (12.95, 33.63, 1.03), (0.45, 0.22, 0.25), mat_cushion_red)

    # 2. Tủ Kính Trưng Bày Gia Phả Dòng Họ & Kỷ Vật Tiền Nhân (Kê sát tường hậu)
    add_box("TuGiaPha_Duoi", (16.05, 32.00, 0.47), (0.68, 2.00, 0.75), mat_wood_dark)
    add_box("TuGiaPha_Kinh", (16.10, 32.05, 1.22), (0.58, 1.90, 1.10), mat_glass)
    add_box("TuGiaPha_Dinh", (16.00, 31.95, 2.32), (0.78, 2.10, 0.08), mat_wood_dark)
    add_box("Sach_GiaPha",   (16.35, 32.60, 1.30), (0.28, 0.40, 0.08), mat_gold)
    add_box("SacPhong_Hop",  (16.35, 33.20, 1.30), (0.15, 0.50, 0.12), mat_lacquer_red)

    # 3. Bức Tranh Thư Pháp "TỔ ĐỨC TRƯỜNG TỒN" trên tường hồi Bắc
    add_box("TranhThuPhap_Khung", (13.60, 34.26, 1.80), (1.40, 0.02, 0.75), mat_lacquer_red)
    add_box("TranhThuPhap_Chu",   (13.75, 34.25, 1.90), (1.10, 0.01, 0.55), mat_gold)

    # =========================================================================
    # HỆ THỐNG CHIẾU SÁNG NỘI THẤT NHÀ 3 GIAN
    # =========================================================================
    add_cylinder("DenLong_GianTa",   (13.8, 27.0, 3.10), 0.18, 0.35, mat_lacquer_red, vertices=6)
    add_light_source("Light_GianTa", (13.8, 27.0, 2.95), energy=35.0, color=(1.0, 0.90, 0.75))

    add_cylinder("DenLong_GianGiua", (14.5, 30.0, 3.30), 0.24, 0.45, mat_gold, vertices=6)
    add_light_source("Light_GianGiua", (14.5, 30.0, 3.10), energy=65.0, color=(1.0, 0.88, 0.65))

    add_cylinder("DenLong_GianHuu",  (13.8, 33.0, 3.10), 0.18, 0.35, mat_lacquer_red, vertices=6)
    add_light_source("Light_GianHuu", (13.8, 33.0, 2.95), energy=35.0, color=(1.0, 0.90, 0.75))

    add_light_source("Spot_BanThoTo", (15.2, 30.0, 2.70), energy=45.0, color=(1.0, 0.85, 0.55))

    # Mái ngói đỏ Nhà 3 Gian Bắc Bộ
    add_gabled_roof("Mai_Nha3Gian", 11.2, 17.5, 25.2, 34.8, 3.45, 4.8, overhang=0.45, material=mat_roof_red)
    add_box("BoNoc_Nha3Gian", (14.25, 25.0, 4.8), (0.25, 10.0, 0.2), mat_blue_stone)
    add_cone("KimNoc_Dau", (14.37, 25.0, 5.0), 0.15, 0.4, mat_gold)
    add_cone("KimNoc_Cuoi", (14.37, 35.0, 5.0), 0.15, 0.4, mat_gold)

    add_box("VuonHong_Khu1", (11.2, 34.7, 0.05), (1.8, 1.1, 0.15), mat_grass)
    add_cylinder("BuiChuoi_1", (13.6, 35.3, 0.0), 0.12, 2.0, mat_grass)
    add_cylinder("BuiChuoi_2", (14.2, 35.5, 0.0), 0.09, 1.6, mat_grass)
    add_box("Toilet_SauNha3Gian", (15.0, 34.5, 0.0), (2.0, 1.5, 2.6), mat_wall)
    add_gabled_roof("Mai_Toilet_Sau", 14.9, 17.1, 34.4, 36.1, 2.6, 3.1, overhang=0.2, material=mat_roof_red)
    add_box("DuongDi1m_Khu1", (11.0, 36.0, 0.01), (7.0, 1.0, 0.04), mat_blue_stone)

    # =========================================================================
    # 6. DÃY BÊN TRÁI (X = 0.0 -> 7.0, Dài 37.0m)
    # =========================================================================
    add_box("DaiLui_Trai_1m", (0.0, 0.0, 0.005), (1.0, 37.0, 0.02), mat_paver_gray)

    # -------------------------------------------------------------------------
    # KHU 4 - NHÀ KHÁCH NGHỈ DƯỠNG GIA TỘC (6.0m x 12.0m, 72m²)
    # Mặt bằng công năng chuẩn biệt thự nghỉ dưỡng truyền thống:
    # 1. Hành lang lưu thông nội bộ dọc theo trục đường 4m (X = 5.56 -> 6.82, Y = 0.18 -> 8.00)
    # 2. Hai phòng ngủ khép kín độc lập, có tường ngăn và cửa đi riêng biệt từ hành lang
    # 3. Đại sảnh Phòng Khách mở thông hoàn toàn từ hành lang (Y = 8.00 -> 12.00, 22.5m²)
    #    hướng trọn vẹn ra ao cá quê qua vách kính panorama kịch trần
    # -------------------------------------------------------------------------
    # Sàn tổng thể Nhà Khách
    add_box("San_NhaKhach", (1.0, 0.0, 0.01), (6.0, 12.0, 0.06), mat_wood_floor)
    
    # Tường bao ngoài Nhà Khách
    add_box("TuongNgoai_Trai_NK", (1.0, 0.0, 0.0), (0.18, 12.0, 3.2), mat_wall)
    add_box("TuongDau_NK",        (1.0, 0.0, 0.0), (6.0, 0.18, 3.2), mat_wall)
    
    # Tường ngoài bên phải (giáp trục đường 4m):
    # Chia làm chân tường (0.8m) giữ lại khi bóc mái để định hình khuôn viên,
    # và phần tường cao phía trên (bắt đầu bằng "Mai_") ẩn đi khi bóc mái để lộ trọn vẹn hành lang & nội thất.
    add_box("TuongNgoai_Phai_NK_Thap",    (6.82, 0.0, 0.0), (0.18, 12.0, 0.8), mat_wall)
    add_box("Mai_TuongNgoai_Phai_NK_Cao", (6.82, 0.0, 0.8), (0.18, 12.0, 2.4), mat_wall)

    # Cửa chính ra vào Nhà Khách từ trục đường 4m (dẫn thẳng vào đầu hành lang)
    add_box("Khung_CuaChinh_NK", (6.78, 0.60, 0.0), (0.06, 1.20, 2.30), mat_wood_dark)
    add_box("CuaChinh_NhaKhach", (6.79, 0.65, 0.05), (0.04, 1.10, 2.20), mat_wood_dark)

    # Mái ngói đỏ Nhà Khách
    add_gabled_roof("Mai_NhaKhach", 0.8, 7.2, 0.0, 12.0, 3.2, 4.4, overhang=0.4, material=mat_roof_red)

    # =========================================================================
    # A. HÀNH LANG NỐI CÁC PHÒNG (X = 5.56 -> 6.82, Y = 0.18 -> 8.00, Rộng 1.26m)
    # =========================================================================
    add_box("San_HanhLang", (5.56, 0.18, 0.015), (1.26, 7.82, 0.05), mat_wood_floor)
    
    # Tường hành lang dọc (dày 0.12m, X = 5.44 -> 5.56, Y = 0.18 -> 8.00):
    # Ngăn cách giữa hành lang và 2 phòng ngủ, trổ 2 cửa đi riêng biệt có khuôn bao & cánh cửa
    # Đoạn tường 1: từ đầu nhà đến mép cửa Phòng 1 (Y = 0.18 -> 2.80)
    add_box("TuongHL_Doan1", (5.44, 0.18, 0.0), (0.12, 2.62, 2.85), mat_wall)
    # Lanh-tô trên cửa Phòng 1 (Y = 2.80 -> 3.70, Z = 2.20 -> 2.85)
    add_box("TuongHL_LanCanh1", (5.44, 2.80, 2.20), (0.12, 0.90, 0.65), mat_wall)
    # Khuôn bao cửa Phòng 1 (gỗ mun / gỗ lim Lào)
    add_box("KhungCua1_Trai", (5.42, 2.80, 0.0), (0.16, 0.05, 2.20), mat_wood_dark)
    add_box("KhungCua1_Phai", (5.42, 3.65, 0.0), (0.16, 0.05, 2.20), mat_wood_dark)
    add_box("KhungCua1_Dinh", (5.42, 2.80, 2.15), (0.16, 0.90, 0.05), mat_wood_dark)
    # Cánh cửa gỗ Phòng 1 mở hé góc 35 độ vào phòng kèm tay nắm gạt sang trọng
    add_door_panel("CanhCua_Phong1", (5.50, 2.85, 0.02), width=0.80, thickness=0.04, height=2.13, angle_deg=35.0, mat_panel=mat_wood_door, mat_handle=mat_brass)

    # Đoạn tường 2: giữa cửa Phòng 1 và cửa Phòng 2 (Y = 3.70 -> 4.30)
    add_box("TuongHL_Doan2", (5.44, 3.70, 0.0), (0.12, 0.60, 2.85), mat_wall)
    
    # Lanh-tô trên cửa Phòng 2 (Y = 4.30 -> 5.20, Z = 2.20 -> 2.85)
    add_box("TuongHL_LanCanh2", (5.44, 4.30, 2.20), (0.12, 0.90, 0.65), mat_wall)
    # Khuôn bao cửa Phòng 2
    add_box("KhungCua2_Trai", (5.42, 4.30, 0.0), (0.16, 0.05, 2.20), mat_wood_dark)
    add_box("KhungCua2_Phai", (5.42, 5.15, 0.0), (0.16, 0.05, 2.20), mat_wood_dark)
    add_box("KhungCua2_Dinh", (5.42, 4.30, 2.15), (0.16, 0.90, 0.05), mat_wood_dark)
    # Cánh cửa gỗ Phòng 2 mở hé góc 35 độ vào phòng kèm tay nắm gạt
    add_door_panel("CanhCua_Phong2", (5.50, 4.35, 0.02), width=0.80, thickness=0.04, height=2.13, angle_deg=35.0, mat_panel=mat_wood_door, mat_handle=mat_brass)

    # Đoạn tường 3: từ mép cửa Phòng 2 đến hết vách ngăn phòng (Y = 5.20 -> 8.00)
    add_box("TuongHL_Doan3", (5.44, 5.20, 0.0), (0.12, 2.80, 2.85), mat_wall)
    
    # Đèn downlight trần và tranh ảnh nghệ thuật treo dọc hành lang
    for yhl, ih in [(1.8, 1), (4.0, 2), (6.2, 3)]:
        add_cylinder(f"DenHL_{ih}", (6.19, yhl, 2.82), 0.08, 0.02, mat_gold)
        add_light_source(f"Light_HL_{ih}", (6.19, yhl, 2.70), energy=22.0, color=(1.0, 0.95, 0.88))
    add_box("TranhHL_1", (5.565, 1.4, 1.3), (0.015, 0.75, 0.55), mat_wood_dark)
    add_box("TranhHL_2", (5.565, 6.2, 1.3), (0.015, 0.75, 0.55), mat_wood_dark)

    # =========================================================================
    # B. PHÒNG NGỦ MASTER 1 KHÉP KÍN (Y = 0.18 -> 3.94, X = 1.18 -> 5.44, 16.5m²)
    # =========================================================================
    # Vách ngăn giữa Phòng 1 và Phòng 2 (tại Y = 3.94 -> 4.06)
    add_box("Vach_Phong1_2", (1.18, 3.94, 0.0), (4.26, 0.12, 2.85), mat_wall)

    # WC Master 1 (X = 1.18 -> 2.68, Y = 0.18 -> 2.08, 2.85m²)
    add_box("Tuong_WC1_Doc",     (2.68, 0.18, 0.0),  (0.10, 1.90, 2.6), mat_wall)
    add_box("Tuong_WC1_Ngang",   (1.18, 2.08, 0.0),  (0.70, 0.10, 2.6), mat_wall)
    add_box("Tuong_WC1_LanCanh", (1.88, 2.08, 2.1),  (0.80, 0.10, 0.5), mat_wall)
    add_box("Khung_CuaWC1",      (1.88, 2.06, 0.0),  (0.80, 0.04, 2.1), mat_wood_dark)
    add_box("Cua_WC1",           (1.92, 2.07, 0.02), (0.72, 0.03, 2.05), mat_wood_dark)

    add_box("San_WC1",           (1.18, 0.18, 0.02), (1.50, 1.90, 0.04), mat_slate_wc)
    add_box("VachKinhTam_WC1",   (1.18, 1.10, 0.05), (1.00, 0.02, 2.1), mat_glass)
    add_cylinder("VoiSen_WC1",   (1.35, 0.45, 1.8),  0.08, 0.35, mat_chrome)
    add_box("Lavabo_Ban_WC1",    (2.05, 0.30, 0.05), (0.55, 0.50, 0.82), mat_black_marble)
    add_cylinder("Lavabo_Chau_WC1", (2.32, 0.55, 0.85), 0.16, 0.12, mat_ceramic_wc)
    add_box("Guong_WC1",         (2.08, 0.20, 1.15), (0.50, 0.02, 0.70), mat_glass)
    add_box("Toilet_WC1",        (2.10, 1.35, 0.05), (0.45, 0.60, 0.45), mat_ceramic_wc)

    # Giường King Size Master 1 (1.8m x 2.0m)
    add_box("Giuong1_Khung",  (3.00, 1.00, 0.05), (1.90, 2.10, 0.40), mat_wood_warm)
    add_box("Giuong1_Nem",    (3.08, 1.08, 0.45), (1.74, 1.94, 0.22), mat_white_linen)
    add_box("Giuong1_Runner", (3.08, 2.45, 0.67), (1.74, 0.48, 0.02), mat_gold_runner)
    add_box("Giuong1_Dau",    (3.00, 0.95, 0.05), (1.90, 0.08, 1.10), mat_wood_dark)
    add_box("Giuong1_Goi1",   (3.25, 1.15, 0.67), (0.55, 0.38, 0.10), mat_pillow)
    add_box("Giuong1_Goi2",   (4.05, 1.15, 0.67), (0.55, 0.38, 0.10), mat_pillow)

    add_box("Tab1_Trai",        (2.45, 1.00, 0.05), (0.45, 0.45, 0.50), mat_wood_dark)
    add_cylinder("DenTab1_Trai", (2.67, 1.22, 0.55), 0.07, 0.32, mat_gold)
    add_box("Tab1_Phai",        (5.00, 1.00, 0.05), (0.35, 0.45, 0.50), mat_wood_dark)
    add_cylinder("DenTab1_Phai", (5.18, 1.22, 0.55), 0.07, 0.32, mat_gold)
    add_light_source("Light_Bed1", (3.95, 2.20, 2.40), energy=35.0, color=(1.0, 0.92, 0.82))

    add_box("TuAo1",        (1.18, 2.30, 0.05), (1.40, 0.60, 2.40), mat_wood_dark)
    add_box("BanLamViec1",  (3.00, 3.45, 0.05), (1.50, 0.45, 0.75), mat_wood_warm)
    add_box("GheLamViec1",  (3.50, 3.10, 0.05), (0.45, 0.45, 0.45), mat_wood_dark)
    add_box("TV1_ManHinh",  (3.20, 3.86, 1.20), (1.10, 0.04, 0.65), mat_wood_dark)

    # =========================================================================
    # C. PHÒNG NGỦ 2 KHÉP KÍN (Y = 4.06 -> 7.94, X = 1.18 -> 5.44, 16.5m²)
    # =========================================================================
    # Vách ngăn phía sau Phòng 2 (tại Y = 7.94 -> 8.06, chỉ từ X = 1.18 đến X = 5.44)
    # Lưu ý: Điểm dừng tại X = 5.44, để đoạn X = 5.44 -> 6.82 mở thông 100% ra phòng khách!
    add_box("Vach_Phong2_Living", (1.18, 7.94, 0.0), (4.26, 0.12, 2.85), mat_wall)

    # WC Phòng 2
    add_box("Tuong_WC2_Doc",     (2.68, 4.06, 0.0),  (0.10, 1.90, 2.6), mat_wall)
    add_box("Tuong_WC2_Ngang",   (1.18, 5.96, 0.0),  (0.70, 0.10, 2.6), mat_wall)
    add_box("Tuong_WC2_LanCanh", (1.88, 5.96, 2.1),  (0.80, 0.10, 0.5), mat_wall)
    add_box("Khung_CuaWC2",      (1.88, 5.94, 0.0),  (0.80, 0.04, 2.1), mat_wood_dark)
    add_box("Cua_WC2",           (1.92, 5.95, 0.02), (0.72, 0.03, 2.05), mat_wood_dark)

    add_box("San_WC2",           (1.18, 4.06, 0.02), (1.50, 1.90, 0.04), mat_slate_wc)
    add_box("VachKinhTam_WC2",   (1.18, 5.00, 0.05), (1.00, 0.02, 2.1), mat_glass)
    add_cylinder("VoiSen_WC2",   (1.35, 4.35, 1.8),  0.08, 0.35, mat_chrome)
    add_box("Lavabo_Ban_WC2",    (2.05, 4.20, 0.05), (0.55, 0.50, 0.82), mat_black_marble)
    add_cylinder("Lavabo_Chau_WC2", (2.32, 4.45, 0.85), 0.16, 0.12, mat_ceramic_wc)
    add_box("Guong_WC2",         (2.08, 4.10, 1.15), (0.50, 0.02, 0.70), mat_glass)
    add_box("Toilet_WC2",        (2.10, 5.25, 0.05), (0.45, 0.60, 0.45), mat_ceramic_wc)

    # 2 Giường đơn Twin Beds (cho con cháu / khách quý)
    add_box("Giuong2A_Khung",  (2.80, 4.80, 0.05), (1.10, 2.00, 0.40), mat_wood_warm)
    add_box("Giuong2A_Nem",    (2.85, 4.85, 0.45), (1.00, 1.90, 0.22), mat_white_linen)
    add_box("Giuong2A_Runner", (2.85, 6.15, 0.67), (1.00, 0.42, 0.02), mat_gold_runner)
    add_box("Giuong2A_Goi",    (2.95, 4.95, 0.67), (0.60, 0.38, 0.10), mat_pillow)

    add_box("Giuong2B_Khung",  (4.25, 4.80, 0.05), (1.10, 2.00, 0.40), mat_wood_warm)
    add_box("Giuong2B_Nem",    (4.30, 4.85, 0.45), (1.00, 1.90, 0.22), mat_white_linen)
    add_box("Giuong2B_Runner", (4.30, 6.15, 0.67), (1.00, 0.42, 0.02), mat_gold_runner)
    add_box("Giuong2B_Goi",    (4.40, 4.95, 0.67), (0.60, 0.38, 0.10), mat_pillow)

    add_box("Tab2_Giua",        (3.92, 4.80, 0.05), (0.31, 0.45, 0.50), mat_wood_dark)
    add_cylinder("DenTab2",     (4.07, 5.02, 0.55), 0.07, 0.32, mat_gold)
    add_light_source("Light_Bed2", (3.95, 5.80, 2.40), energy=35.0, color=(1.0, 0.92, 0.82))

    add_box("TuAo2",     (1.18, 6.18, 0.05), (1.40, 0.60, 2.40), mat_wood_dark)
    add_box("KeHanhLy2", (1.18, 6.95, 0.05), (1.20, 0.50, 0.45), mat_wood_warm)
    add_box("TV2_ManHinh", (3.20, 7.86, 1.20), (1.10, 0.04, 0.65), mat_wood_dark)

    # =========================================================================
    # D. ĐẠI SẢNH PHÒNG KHÁCH MỞ THÔNG HÀNH LANG & NGẮM AO CÁ (Y = 8.00 -> 12.00)
    # Rộng 5.64m x Dài 4.00m = 22.56 m². Không gian mở hoàn toàn, không vách ngăn hành lang
    # Kết nối trọn vẹn từ hành lang vào phòng khách như không gian nhà ở hiện đại
    # =========================================================================
    add_box("San_PhongKhach_Open", (1.18, 8.00, 0.015), (5.64, 3.96, 0.05), mat_wood_floor)
    add_box("Tham_PhongKhach",     (1.80, 9.10, 0.065), (3.60, 2.30, 0.005), mat_rug)

    # 1. Quầy Tiện Ích Mini-Pantry & Bar Trà (Góc sau bên trái tựa vào vách phòng ngủ)
    add_box("Pantry_TuGo",       (1.25, 8.12, 0.07), (1.90, 0.55, 0.85), mat_wood_dark)
    add_box("Pantry_MatDa",      (1.23, 8.10, 0.92), (1.94, 0.59, 0.04), mat_black_marble)
    add_box("Pantry_TuLanh",     (1.30, 8.14, 0.10), (0.48, 0.48, 0.75), mat_chrome)
    add_cylinder("Pantry_AmSieuToc", (2.00, 8.35, 0.96), 0.07, 0.22, mat_chrome)
    add_box("Pantry_KeLy",       (1.25, 8.12, 1.60), (1.90, 0.25, 0.55), mat_wood_warm)

    # 2. Bộ Bàn Ghế Phòng Khách Sang Trọng (Trường Kỷ / Sofa Gỗ Tự Nhiên)
    # Ghế sofa văng dài 3-4 chỗ (ngồi nhìn thẳng ra mặt ao cá làng quê)
    add_box("Sofa_KhungGo", (1.80, 9.25, 0.07), (2.60, 0.85, 0.38), mat_wood_warm)
    add_box("Sofa_TuaLung", (1.80, 9.25, 0.45), (2.60, 0.18, 0.35), mat_wood_warm)
    add_box("Sofa_DemNgoi", (1.88, 9.43, 0.42), (2.44, 0.62, 0.12), mat_cushion)
    add_box("Sofa_Goi1",    (2.05, 9.38, 0.54), (0.45, 0.15, 0.25), mat_pillow)
    add_box("Sofa_Goi2",    (2.85, 9.38, 0.54), (0.45, 0.15, 0.25), mat_gold_runner)
    add_box("Sofa_Goi3",    (3.65, 9.38, 0.54), (0.45, 0.15, 0.25), mat_pillow)
    add_box("Sofa_TayTrai", (1.75, 9.25, 0.42), (0.13, 0.85, 0.22), mat_wood_warm)
    add_box("Sofa_TayPhai", (4.40, 9.25, 0.42), (0.13, 0.85, 0.22), mat_wood_warm)

    # Bàn trà phòng khách (Gỗ tự nhiên me tây nguyên tấm)
    add_box("BanTra_Chan", (2.30, 10.35, 0.07), (1.60, 0.50, 0.32), mat_wood_dark)
    add_box("BanTra_Mat",  (2.10, 10.25, 0.39), (2.00, 0.70, 0.06), mat_wood_warm)

    # Bộ ấm chén Bát Tràng truyền thống trên bàn trà
    add_box("KhayTra_Gom", (2.70, 10.45, 0.45), (0.60, 0.35, 0.03), mat_wood_dark)
    add_cylinder("AmTra_Gom", (2.90, 10.60, 0.48), 0.06, 0.09, mat_tea_pot)
    for icp in range(4):
        c_ang = math.radians(icp * 90)
        add_cylinder(f"ChenTra_{icp}", (3.15 + 0.08*math.cos(c_ang), 10.60 + 0.08*math.sin(c_ang), 0.48), 0.025, 0.03, mat_ceramic_wc)

    # 2 Ghế đơn Armchair thư giãn góc nhìn ao cá
    add_box("GheDon1_Khung", (4.80, 9.45, 0.07), (0.75, 0.75, 0.38), mat_wood_warm)
    add_box("GheDon1_Dem",   (4.85, 9.50, 0.42), (0.65, 0.65, 0.12), mat_cushion)
    add_box("GheDon1_Tua",   (5.40, 9.45, 0.45), (0.15, 0.75, 0.35), mat_wood_warm)

    add_box("GheDon2_Khung", (4.80, 10.45, 0.07), (0.75, 0.75, 0.38), mat_wood_warm)
    add_box("GheDon2_Dem",   (4.85, 10.50, 0.42), (0.65, 0.65, 0.12), mat_cushion)
    add_box("GheDon2_Tua",   (5.40, 10.45, 0.45), (0.15, 0.75, 0.35), mat_wood_warm)
    add_cylinder("BanPhu_GheDon", (5.15, 10.35, 0.07), 0.18, 0.48, mat_wood_dark)

    # Kệ trang trí & Bonsai mini dọc vách tường bên trái
    add_box("KeTrangTri_PK", (1.22, 9.60, 0.07), (0.35, 1.50, 0.55), mat_wood_dark)
    add_cylinder("Bonsai_Chau", (1.38, 10.10, 0.62), 0.12, 0.08, mat_ceramic_wc)
    add_cylinder("Bonsai_Than", (1.38, 10.10, 0.70), 0.03, 0.20, mat_wood_dark)
    add_sphere("Bonsai_Tan",    (1.38, 10.10, 0.92), radius=0.15, scale=(1.2, 1.2, 0.7), material=mat_grass)
    add_cylinder("LoHoa_Sen",   (1.38, 10.70, 0.62), 0.06, 0.22, mat_ceramic_wc)

    # VÁCH KÍNH TRÀN VIỀN KỊCH TRẦN VIEW AO CÁ (tại Y = 11.97, rộng 5.64m x cao 3.15m)
    add_box("Kinh_ViewAo_OpenLiving", (1.18, 11.97, 0.05), (5.64, 0.02, 3.15), mat_glass)
    add_cylinder("DoKhung_Kinh_Trai", (1.18, 11.97, 0.05), 0.035, 3.15, mat_wood_dark)
    add_cylinder("DoKhung_Kinh_Phai", (6.82, 11.97, 0.05), 0.035, 3.15, mat_wood_dark)
    add_box("XaNgang_Kinh_Tren",      (1.18, 11.96, 2.85), (5.64, 0.05, 0.05), mat_wood_dark)

    # Đèn chùm trung tâm phòng khách & nguồn sáng ấm
    add_cylinder("DenChum_PhongKhach", (3.20, 10.50, 2.30), 0.25, 0.35, mat_wood_warm)
    add_light_source("Light_PhongKhach", (3.20, 10.50, 2.15), energy=55.0, color=(1.0, 0.92, 0.80))

    # -------------------------------------------------------------------------
    # KHU 5 - CÁI AO CÁ BÌNH THƯỜNG / VƯỜN QUÊ DÂN DÃ (6.0m x 5.0m, 30 m²)
    # Lòng ao sâu -0.70m, nước xanh mát trong tự nhiên, bờ kè đá cuội mộc mạc,
    # đàn cá đồng / cá chép quê bơi lội, cụm hoa sen, hoa súng và cầu ao gỗ lim
    # -------------------------------------------------------------------------
    # 1. Đáy ao và thành ao rỗng (Hollow pond basin sâu -0.70m)
    add_box("DayAo_SanDatCat", (1.15, 12.15, -0.70), (5.7, 4.7, 0.05), mat_pond_bottom)
    add_box("ThanhAo_Nam",     (1.15, 12.00, -0.70), (5.7, 0.15, 0.70), mat_pond_wall)
    add_box("ThanhAo_Bac",     (1.15, 16.85, -0.70), (5.7, 0.15, 0.70), mat_pond_wall)
    add_box("ThanhAo_Tay",     (1.00, 12.00, -0.70), (0.15, 5.0, 0.70), mat_pond_wall)
    add_box("ThanhAo_Dong",    (6.85, 12.00, -0.70), (0.15, 5.0, 0.70), mat_pond_wall)

    # 2. Bờ kè đá cuội sông tự nhiên quanh 4 mép bờ ao
    for ix in range(9):
        rx = 1.35 + ix * 0.62
        add_sphere(f"DaBoAo_Nam_{ix}", (rx, 12.06, -0.04), radius=0.20, scale=(1.2, 0.9, 0.65), material=mat_rock_river)
    for ix in range(9):
        rx = 1.35 + ix * 0.62
        add_sphere(f"DaBoAo_Bac_{ix}", (rx, 16.94, -0.04), radius=0.22, scale=(1.1, 0.8, 0.70), material=mat_rock_river)
    for iy in range(7):
        ry = 12.5 + iy * 0.65
        add_sphere(f"DaBoAo_Tay_{iy}", (1.14, ry, -0.04), radius=0.22, scale=(0.8, 1.2, 0.65), material=mat_rock_river)
    for iy in range(7):
        ry = 12.5 + iy * 0.65
        add_sphere(f"DaBoAo_Dong_{iy}", (6.86, ry, -0.04), radius=0.22, scale=(0.85, 1.1, 0.65), material=mat_rock_river)

    # 3. MẶT NƯỚC AO CÁ QUÊ: Xanh mát trong tự nhiên (Cao độ Z = -0.10m)
    add_box("MatNuoc_AoCa_TrongSuot", (1.16, 12.16, -0.10), (5.68, 4.68, 0.04), mat_water)

    # 4. ĐÀN CÁ CHÉP ĐỒNG / CÁ AO BÌNH THƯỜNG (Bơi lội dưới làn nước trong Z = -0.14m -> -0.18m)
    carp_data = [
        # (name, loc, yaw, scale, mat_body, mat_fin)
        ("CaChep_Bac1",   (3.1, 13.0, -0.14), 55.0,  0.85, mat_carp_silver, mat_carp_fin),
        ("CaChep_VangDong",(4.1, 13.3, -0.13), -40.0, 0.90, mat_carp_gold,   mat_carp_fin),
        ("CaChep_Bac2",   (3.6, 14.1, -0.15), 125.0, 0.80, mat_carp_silver, mat_carp_fin),
        ("CaChep_DoQue1", (4.8, 13.9, -0.14), -75.0, 0.75, mat_carp_red,    mat_carp_fin),
        ("CaChep_Dong3",  (2.5, 14.2, -0.15), 15.0,  0.82, mat_carp_silver, mat_carp_fin),
        ("CaChep_Vang2",  (4.4, 14.8, -0.14), -120.0,0.85, mat_carp_gold,   mat_carp_fin),
        ("CaChep_DoQue2", (3.4, 15.2, -0.15), 85.0,  0.78, mat_carp_red,    mat_carp_fin),
        ("CaChep_Bac4",   (2.2, 13.6, -0.15), 60.0,  0.75, mat_carp_silver, mat_carp_fin),
    ]
    for c_name, c_loc, c_yaw, c_sc, c_mb, c_mf in carp_data:
        add_carp_fish(c_name, c_loc, c_yaw, c_sc, c_mb, c_mf)

    # Nguồn sáng chiếu nhẹ làm rõ mặt nước ao quê
    add_light_source("Light_AoCa_Fill", (3.8, 13.8, 0.20), energy=40.0, color=(0.92, 0.98, 0.95))

    # 5. CỤM HOA SEN & HOA SÚNG AO LÀNG
    lotus_clusters = [
        ("Sen_Cum1_TayNam", (1.8, 13.2, -0.09)),
        ("Sen_Cum2_DongBac", (5.5, 15.8, -0.09)),
        ("Sen_Cum3_GiuaTay", (1.8, 15.5, -0.09)),
        ("Sen_Cum4_GocDong", (5.8, 13.6, -0.09))
    ]
    for c_name, c_pos in lotus_clusters:
        add_lotus_cluster(c_name, c_pos, mat_lotus_leaf, mat_lotus_pink, mat_lotus_yellow)

    # 6. CẦU AO GỖ LIM TRUYỀN THỐNG BẮC RA MÉP NƯỚC (Nét văn hóa Cầu Ao giếng nước sân đình)
    add_box("CauAo_GoLim", (4.8, 12.0, 0.01), (1.4, 1.8, 0.06), mat_wood_deck)
    # Cọc cắm đỡ cầu ao bằng gỗ lim
    for (cx, cy) in [(4.9, 13.6), (6.1, 13.6)]:
        add_cylinder(f"CocCauAo_{cx}", (cx, cy, -0.65), 0.05, 0.70, mat_wood_dark)

    # 7. KHÓM THỦY TRÚC & BỜ CỎ DÂN DÃ VEN AO (Góc giáp Khu 6)
    for ytt in [16.2, 16.5, 16.8]:
        add_cylinder(f"ThuyTruc_{ytt}", (1.4, ytt, 0.0), 0.02, 1.8, mat_grass)
        add_cone(f"LaThuyTruc_{ytt}", (1.4, ytt, 1.5), 0.25, 0.6, mat_grass)

    # --- KHU 6: VƯỜN CÂY CẢNH QUAN (X = 1.0 -> 7.0, Y = 17.0 -> 33.0, 96m²) ---
    add_box("ThamCo_VuonKhu6", (1.0, 17.0, 0.01), (6.0, 16.0, 0.03), mat_grass)
    path_points = [
        (4.0, 17.8), (3.6, 19.5), (4.2, 21.2), (4.8, 23.0),
        (3.8, 25.0), (3.5, 27.2), (4.3, 29.5), (4.0, 31.8)
    ]
    for idx, (px, py) in enumerate(path_points):
        add_cylinder(f"DaBuocDao_{idx}", (px, py, 0.03), 0.40, 0.04, mat_blue_stone)

    trees_data = [
        ("CayBuoi_1",    (2.4, 19.2, 0.0), 0.22, 3.6, 1.7),
        ("CayMocHuong",  (5.6, 21.5, 0.0), 0.18, 3.2, 1.5),
        ("CayKheNgot",   (2.2, 25.0, 0.0), 0.24, 3.8, 1.9),
        ("CayMaiVang",   (5.5, 28.0, 0.0), 0.16, 3.0, 1.4),
        ("CayBuoi_2",    (2.6, 31.2, 0.0), 0.20, 3.4, 1.6),
    ]
    for t_name, loc, tr, h, fr in trees_data:
        add_tree(t_name, loc, tr, h, fr, mat_wood_dark, mat_grass)

    # --- KHU 7: QUỸ ĐẤT DỰ TRỮ (X = 1.0 -> 7.0, Y = 33.0 -> 37.0, 24m²) ---
    add_box("San_DuTru_Khu7", (1.0, 33.0, 0.01), (6.0, 4.0, 0.04), mat_grass)
    add_box("VienBo_DuTru",   (1.0, 33.0, 0.03), (6.0, 0.15, 0.10), mat_blue_stone)

    # =========================================================================
    # 7. ÁNH SÁNG MẶT TRỜI TỰ NHIÊN
    # =========================================================================
    bpy.ops.object.light_add(type='SUN', location=(20.0, -12.0, 30.0))
    sun = bpy.context.active_object
    sun.name = "MatTroi_Chinh"
    sun.data.energy = 5.5
    sun.data.color = (1.0, 0.97, 0.92)
    sun.data.angle = math.radians(2.0)
    sun.rotation_euler = (math.radians(50), math.radians(16), math.radians(-35))

    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Sky")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.75, 0.86, 0.98, 1.0)
        bg.inputs['Strength'].default_value = 1.30

    # =========================================================================
    # 8. THIẾT LẬP 6 GÓC CAMERA CHUYÊN NGHIỆP
    # =========================================================================
    def setup_camera(name, loc, target_loc, focal_length=35):
        bpy.ops.object.camera_add(location=loc)
        cam = bpy.context.active_object
        cam.name = name
        cam.data.lens = focal_length
        cam.data.clip_end = 200.0

        bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_loc)
        tgt = bpy.context.active_object
        tgt.name = f"Tgt_{name}"

        constraint = cam.constraints.new(type='TRACK_TO')
        constraint.target = tgt
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        return cam

    # 1. Phối cảnh tổng thể từ trên cao nhìn vào cổng
    setup_camera("Cam_1_TongThe", (26.0, -14.0, 24.0), (9.0, 18.5, 1.5), focal_length=28)
    
    # 2. Phối cảnh bóc mái nhìn toàn bộ công năng nội thất
    setup_camera("Cam_2_BocMai", (22.0, -5.0, 25.0), (6.5, 14.5, 1.0), focal_length=30)

    # 3. Cận cảnh Đài Lục Giác 6m & Nhà 3 Gian Bắc Bộ
    setup_camera("Cam_3_DaiLucGiac_Nha3Gian", (3.0, 15.0, 7.5), (14.0, 23.5, 2.5), focal_length=32)

    # 4. Hành lang kỷ vật xưa & Bàn ăn thông minh qua vách kính
    setup_camera("Cam_4_KyVat_NhaAn", (13.2, 4.0, 1.6), (17.4, 8.0, 1.0), focal_length=28)

    # 5. ĐẶC BIỆT: Từ Phòng Khách Đại Sảnh nhìn ra ao cá quê thanh bình qua vách kính panorama
    # Vị trí đặt máy góc rộng (22mm) thấy trọn vẹn bộ bàn trà, sofa phòng khách và toàn cảnh ao cá
    setup_camera("Cam_5_ViewAo_PhongNgam", (3.0, 8.8, 1.25), (3.8, 14.5, 0.10), focal_length=22)

    # 6. Phối cảnh cổng chính mở rộng nhìn sâu vào trục đường 4m và nhà thờ tổ
    setup_camera("Cam_6_CongChinh", (9.0, -7.5, 1.8), (9.0, 16.0, 1.6), focal_length=28)

    # 7. PHỐI CẢNH NỘI BỘ HÀNH LANG NHÀ KHÁCH:
    # Đứng từ đầu hành lang nhìn xuyên suốt: thấy các cửa phòng ngủ có cánh & tay nắm gạt,
    # phía cuối hành lang mở toang thông suốt vào đại sảnh phòng khách ngắm ao cá
    setup_camera("Cam_7_HanhLang_NhaKhach", (6.19, 0.45, 1.55), (5.50, 11.20, 1.20), focal_length=22)

    # 8. CẬN CẢNH NỘI THẤT NHÀ 3 GIAN BẮC BỘ TRUYỀN THỐNG:
    # Đứng từ hiên gian giữa nhìn thẳng vào gian thờ: thấy ban thờ đại an gian thếp vàng,
    # cửa võng, hoành phi câu đối, lư đồng, đôi hạc, trường kỷ gian tả và sập gụ gian hữu
    setup_camera("Cam_8_NoiThat_Nha3Gian", (11.0, 30.0, 1.55), (15.5, 30.0, 1.65), focal_length=18)

    # 9. PHỐI CẢNH HƯỚNG NAM (Nhìn từ phía Nam ngoài cổng chính vào toàn bộ khuôn viên):
    setup_camera("Cam_Huong_Nam", (9.0, -14.0, 12.0), (9.0, 18.5, 2.0), focal_length=28)

    # 10. PHỐI CẢNH HƯỚNG BẮC (Nhìn từ phía Bắc cuối khu đất sau Nhà 3 Gian về cổng):
    setup_camera("Cam_Huong_Bac", (9.0, 50.0, 14.0), (9.0, 18.5, 2.0), focal_length=28)

    # 11. PHỐI CẢNH HƯỚNG ĐÔNG (Nhìn từ phía Đông bên phải khu đất sang phía Tây):
    setup_camera("Cam_Huong_Dong", (34.0, 18.5, 14.0), (9.0, 18.5, 2.0), focal_length=28)

    # 12. PHỐI CẢNH HƯỚNG TÂY (Nhìn từ phía Tây bên trái khu đất sang phía Đông):
    setup_camera("Cam_Huong_Tay", (-16.0, 18.5, 14.0), (9.0, 18.5, 2.0), focal_length=28)

    # Lưu tệp dự án .blend
    blend_path = "d:/Work/Khu_Nha_Dong_Ho/khu_nha_dong_ho.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f">>> [BLENDER] Đã lưu thành công tệp dự án: {blend_path}")

# =============================================================================
# THIẾT LẬP RENDER CYCLES
# =============================================================================
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 36
if hasattr(bpy.context.scene.cycles, 'use_denoising'):
    bpy.context.scene.cycles.use_denoising = True

bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.image_settings.file_format = 'PNG'

if __name__ == "__main__":
    build_compound()
