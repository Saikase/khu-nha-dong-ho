"""
=============================================================================
MÔ HÌNH 3D SIÊU THỰC - KHU NHÀ DÒNG HỌ TRUYỀN THỐNG VIỆT NAM (18m x 37m)
BLENDER 4.2+ CYCLES ENGINE (QUY HOẠCH NÂNG CẤP MỚI)
- Đường chính mở rộng 8.0m (X = 5.0 -> 13.0m)
- Dãy Trái (X = 0.0 -> 5.0m): 2 Căn Nhà 6x4 liền nhau -> Ao Cá Quê 5m -> Căn Nhà 3 (6x4) -> Vườn Cây 14m
- Dãy Phải (X = 13.0 -> 18.0m): Bếp & Nhà Ăn (13.5m) -> Chòi Vuông 4m x 4m (12m) -> Nhà 3 Gian (11.5m)
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
    return obj

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

def add_pyramid_roof(name, x_min, x_max, y_min, y_max, z_base, z_top, overhang=0.35, material=None):
    """Tạo mái chóp 4 mái hình vuông (tứ giác) cho chòi vuông"""
    x1 = x_min - overhang
    x2 = x_max + overhang
    y1 = y_min - overhang
    y2 = y_max + overhang
    xm = (x_min + x_max) / 2.0
    ym = (y_min + y_max) / 2.0
    
    verts = [
        (x1, y1, z_base),
        (x2, y1, z_base),
        (x2, y2, z_base),
        (x1, y2, z_base),
        (xm, ym, z_top)
    ]
    faces = [
        (0, 1, 4),
        (1, 2, 4),
        (2, 3, 4),
        (3, 0, 4),
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
    for dx, dy in [(-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)]:
        add_cylinder(f"{name}_chan_{dx}_{dy}", (lx+dx, ly+dy, lz), 0.022, 0.45, mat)
    add_box(f"{name}_dem", (lx-0.20, ly-0.20, lz+0.43), (0.40, 0.40, 0.05), mat)
    add_box(f"{name}_tua", (lx-0.20, ly+0.16, lz+0.45), (0.40, 0.04, 0.42), mat)

def add_light_source(name, location, energy=20.0, color=(1.0, 0.90, 0.75), light_type='POINT'):
    """Thêm nguồn sáng điểm/khu vực ấm cúng cho nội thất"""
    bpy.ops.object.light_add(type=light_type, location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.color = color
    return light

def add_carp_fish(name, location, yaw_deg=0.0, scale=0.75, mat_body=None, mat_fin=None):
    """Tạo chú cá chép đồng / cá ao quê tự nhiên bơi lội"""
    lx, ly, lz = location
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.16, location=(lx, ly, lz))
    body = bpy.context.active_object
    body.name = f"{name}_body"
    body.scale = (scale * 0.50, scale * 2.4, scale * 0.85)
    body.rotation_euler = (0, 0, math.radians(yaw_deg))
    bpy.ops.object.shade_smooth()
    if mat_body:
        body.data.materials.append(mat_body)

    rad = math.radians(yaw_deg)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.04 * scale, depth=0.25 * scale, location=(lx, ly, lz + 0.12 * scale))
    dorsal = bpy.context.active_object
    dorsal.name = f"{name}_dorsal"
    dorsal.rotation_euler = (0, math.radians(20), rad)
    dorsal.scale = (0.1, 1.2, 0.8)
    bpy.ops.object.shade_smooth()
    if mat_fin:
        dorsal.data.materials.append(mat_fin)

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

def add_lotus_cluster(name, center, mat_leaf, mat_petal, mat_yellow):
    """Cụm hoa súng / sen ao làng truyền thống"""
    cx, cy, cz = center
    leaf_offsets = [
        (0.0, 0.0, 0.38, 0.0),
        (0.42, -0.25, 0.32, 0.01),
        (-0.40, 0.30, 0.36, -0.01),
        (0.32, 0.40, 0.28, 0.01)
    ]
    for idx, (ox, oy, r, dz) in enumerate(leaf_offsets):
        add_cylinder(f"{name}_la_{idx}", (cx + ox, cy + oy, cz + dz), r, 0.012, mat_leaf, vertices=20)

    fx, fy, fz = cx + 0.08, cy + 0.08, cz + 0.05
    add_cylinder(f"{name}_cuong", (fx, fy, cz - 0.25), 0.016, 0.30, mat_leaf)
    add_cylinder(f"{name}_nhuy", (fx, fy, fz + 0.02), 0.06, 0.035, mat_yellow)
    for ip in range(8):
        pang = math.radians(ip * 45)
        px = fx + 0.10 * math.cos(pang)
        py = fy + 0.10 * math.sin(pang)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.055, depth=0.14, location=(px, py, fz + 0.03))
        petal = bpy.context.active_object
        petal.name = f"{name}_canh_{ip}"
        petal.rotation_euler = (math.radians(35) * math.sin(pang), -math.radians(35) * math.cos(pang), pang)
        bpy.ops.object.shade_smooth()
        petal.data.materials.append(mat_petal)


def build_compound():
    print(">>> [BLENDER] Khởi tạo mô hình Khu Nhà Dòng Họ - Đường 8m & Nhà Vuông...")
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
    
    # Màu nước ao xanh dương rực rỡ & dễ nhận diện
    mat_pond_bottom = create_pbr_material("Nature_DayAoDatCat",   (0.12, 0.38, 0.65, 1.0), roughness=0.65)
    mat_pond_wall   = create_pbr_material("Nature_BoAoDatKeDa",   (0.20, 0.42, 0.58, 1.0), roughness=0.60)
    mat_water       = create_pbr_material("Nature_NuocAoQue",     (0.02, 0.46, 0.90, 1.0), roughness=0.06, transmission=0.65, ior=1.333, emission_color=(0.02, 0.32, 0.72, 1.0), emission_strength=0.25)
    
    # Vật liệu Nhà Ăn Mái Lá & Cầu Ao Bến Giặt Xưa
    mat_thatch_leaf = create_pbr_material("Roof_MaiLaQue",        (0.62, 0.46, 0.22, 1.0), roughness=0.92)
    mat_thatch_ridge= create_pbr_material("Roof_NepBoNocLa",      (0.44, 0.30, 0.14, 1.0), roughness=0.95)
    mat_bamboo      = create_pbr_material("Wood_TreTrucQue",      (0.45, 0.48, 0.22, 1.0), roughness=0.45)
    mat_wash_stone  = create_pbr_material("Stone_PhienDaGiat",    (0.35, 0.42, 0.48, 1.0), roughness=0.25)
    mat_wash_tub    = create_pbr_material("Metal_ThauDongGiat",   (0.85, 0.64, 0.20, 1.0), roughness=0.30, metallic=0.82)
    mat_cotton_cloth= create_pbr_material("Int_VaiChamGiat",      (0.18, 0.26, 0.45, 1.0), roughness=0.85)
    
    mat_glass       = create_pbr_material("Arch_KinhCuongLuc",    (0.92, 0.97, 1.00, 1.0), roughness=0.02, transmission=0.96, ior=1.52)
    mat_gold        = create_pbr_material("Deco_ThepVang9999",    (0.95, 0.75, 0.10, 1.0), roughness=0.22, metallic=0.85)
    mat_pebble      = create_pbr_material("Stone_SoiCuoiTrang",   (0.92, 0.92, 0.88, 1.0), roughness=0.68)
    mat_rock_river  = create_pbr_material("Stone_DaCuoiBoAo",    (0.52, 0.50, 0.46, 1.0), roughness=0.55)
    mat_clay_mill   = create_pbr_material("Deco_DatNenCoiXay",    (0.45, 0.32, 0.20, 1.0), roughness=0.88)
    
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
    
    mat_lacquer_red     = create_pbr_material("Deco_SonSonDo",        (0.75, 0.08, 0.05, 1.0), roughness=0.25)
    mat_terracotta_floor= create_pbr_material("Floor_GachBatTrang",   (0.58, 0.22, 0.10, 1.0), roughness=0.55)
    mat_mat_rush        = create_pbr_material("Int_ChieuCoiHoa",      (0.85, 0.78, 0.58, 1.0), roughness=0.85)
    mat_cushion_red     = create_pbr_material("Int_GoiGamDo",         (0.80, 0.10, 0.12, 1.0), roughness=0.45)
    mat_bronze          = create_pbr_material("Metal_DongHunCo",      (0.35, 0.28, 0.18, 1.0), roughness=0.30, metallic=0.75)
    
    mat_carp_silver = create_pbr_material("Ca_ChepDongBac", (0.55, 0.58, 0.56, 1.0), roughness=0.25, metallic=0.35, emission_color=(0.60, 0.65, 0.60, 1.0), emission_strength=0.3)
    mat_carp_gold   = create_pbr_material("Ca_ChepVangDong", (0.75, 0.55, 0.20, 1.0), roughness=0.25, metallic=0.30, emission_color=(0.80, 0.58, 0.20, 1.0), emission_strength=0.35)
    mat_carp_red    = create_pbr_material("Ca_ChepDoQue",   (0.88, 0.28, 0.08, 1.0), roughness=0.25, emission_color=(0.90, 0.30, 0.08, 1.0), emission_strength=0.4)
    mat_carp_fin    = create_pbr_material("Ca_VayCa",       (0.70, 0.40, 0.18, 1.0), roughness=0.30, emission_color=(0.70, 0.40, 0.18, 1.0), emission_strength=0.2)
    
    mat_lotus_leaf  = create_pbr_material("Lotus_LaSen",    (0.08, 0.42, 0.12, 1.0), roughness=0.40)
    mat_lotus_pink  = create_pbr_material("Lotus_CanhSen",  (0.95, 0.38, 0.55, 1.0), roughness=0.30, emission_color=(0.95, 0.38, 0.55, 1.0), emission_strength=0.15)
    mat_lotus_yellow= create_pbr_material("Lotus_NhuyVang", (0.98, 0.85, 0.08, 1.0), roughness=0.25, emission_color=(0.98, 0.85, 0.08, 1.0), emission_strength=0.25)

    # =========================================================================
    # 2. ĐẤT NỀN BỐI CẢNH NGOÀI RANH ĐẤT
    # =========================================================================
    add_box("Co_Ngoai_Nam", (-10.0, -10.0, -0.2), (38.0, 10.0, 0.2), mat_grass)
    add_box("Co_Ngoai_Bac", (-10.0, 37.0, -0.2),  (38.0, 10.0, 0.2), mat_grass)
    add_box("Co_Ngoai_Tay", (-10.0, 0.0, -0.2),   (10.0, 37.0, 0.2), mat_grass)
    add_box("Co_Ngoai_Dong", (18.0, 0.0, -0.2),   (10.0, 37.0, 0.2), mat_grass)

    # =========================================================================
    # 3. TRỤC ĐƯỜNG CHÍNH MỞ RỘNG 8.0m XUYÊN SUỐT 37.0m (X = 5.0 -> 13.0m)
    # =========================================================================
    add_box("DuongChinh_8m", (5.0, 0.0, 0.01), (8.0, 37.0, 0.03), mat_road_basalt)
    add_box("BoVia_Trai_8m", (4.88, 0.0, 0.0), (0.12, 37.0, 0.06), mat_blue_stone)
    add_box("BoVia_Phai_8m", (13.0, 0.0, 0.0), (0.12, 37.0, 0.06), mat_blue_stone)

    # Cột đèn đá dẫn lối 2 bên trục 8m
    for yd in range(3, 36, 6):
        add_cylinder(f"DenDa_Phai_{yd}", (13.2, yd, 0.0), 0.10, 1.1, mat_blue_stone)
        add_box(f"LongDen_Phai_{yd}", (13.12, yd-0.08, 1.05), (0.16, 0.16, 0.22), mat_gold)
        add_cylinder(f"DenDa_Trai_{yd}", (4.8, yd, 0.0), 0.10, 1.1, mat_blue_stone)
        add_box(f"LongDen_Trai_{yd}", (4.72, yd-0.08, 1.05), (0.16, 0.16, 0.22), mat_gold)

    # =========================================================================
    # 4. TƯỜNG RÀO RANH ĐẤT & CỔNG TAM QUAN 8.0M MỞ RỘNG
    # =========================================================================
    hw = 2.4  # chiều cao tường bao
    tw = 0.22 # độ dày tường
    add_box("TuongRao_Trai", (-tw, 0.0, 0.0), (tw, 37.0, hw), mat_wall)
    add_box("TuongRao_Phai", (18.0, 0.0, 0.0), (tw, 37.0, hw), mat_wall)
    add_box("TuongRao_Sau",  (-tw, 37.0, 0.0), (18.0 + 2*tw, tw, hw), mat_wall)
    add_box("TuongRao_Tien_Trai", (-tw, -tw, 0.0), (5.0 + tw, tw, hw), mat_wall)
    add_box("TuongRao_Tien_Phai", (13.0, -tw, 0.0), (5.0 + tw, tw, hw), mat_wall)

    add_box("MuNgoi_Trai", (-tw - 0.06, -tw, hw), (tw + 0.12, 37.0 + tw, 0.08), mat_roof_red)
    add_box("MuNgoi_Phai", (18.0 - 0.06, -tw, hw), (tw + 0.12, 37.0 + tw, 0.08), mat_roof_red)
    add_box("MuNgoi_Sau",  (-tw, 37.0 - 0.06, hw), (18.0 + 2*tw, tw + 0.12, 0.08), mat_roof_red)
    add_box("MuNgoi_Tien_Trai", (-tw, -tw - 0.06, hw), (5.0 + tw, tw + 0.12, 0.08), mat_roof_red)
    add_box("MuNgoi_Tien_Phai", (13.0, -tw - 0.06, hw), (5.0 + tw, tw + 0.12, 0.08), mat_roof_red)

    # Cổng Tam Quan mở rộng tương xứng với đường 8m
    add_box("TruCong_Trai", (4.55, -0.55, 0.0), (0.75, 0.75, 4.4), mat_blue_stone)
    add_box("TruCong_Phai", (12.70, -0.55, 0.0), (0.75, 0.75, 4.4), mat_blue_stone)
    add_cone("BupSen_Cong_Trai", (4.92, -0.17, 4.4), 0.30, 0.60, mat_blue_stone)
    add_cone("BupSen_Cong_Phai", (13.07, -0.17, 4.4), 0.30, 0.60, mat_blue_stone)
    add_box("XaNgang_Cong", (4.90, -0.35, 3.5), (8.2, 0.40, 0.50), mat_wood_dark)
    add_box("HoanhPhi_Cong", (7.5, -0.42, 3.55), (3.0, 0.08, 0.40), mat_gold)
    add_gabled_roof("Mai_CongChinh", 4.6, 13.4, -0.75, 0.20, 3.95, 4.75, overhang=0.4, material=mat_roof_red)
    add_box("CanhCong_Trai", (5.0, 0.0, 0.0), (0.08, 3.2, 3.3), mat_wood_dark)
    add_box("CanhCong_Phai", (12.92, 0.0, 0.0), (0.08, 3.2, 3.3), mat_wood_dark)

    # =========================================================================
    # 5. DÃY BÊN PHẢI (X = 13.0 -> 18.0, Rộng 5.0m, Dài 37.0m)
    # Rút gọn bề ngang nhà còn 4.0m (X = 13.0 -> 17.0), dải lùi 1m (X = 17.0 -> 18.0)
    # =========================================================================
    add_box("DaiLui_Phai_1m", (17.0, 0.0, 0.005), (1.0, 37.0, 0.02), mat_paver_gray)

    # --- KHU 3: BẾP, 2 WC & NHÀ ĂN GIA TỘC (Y = 0 -> 13.5m) ---
    add_box("WC_Khu3_Tuong", (17.0, 0.0, 0.0), (1.0, 3.0, 2.8), mat_wall)
    add_box("WC_VachNgan",   (17.0, 1.5, 0.0), (1.0, 0.12, 2.8), mat_wall)
    add_box("WC_Cua1", (16.98, 0.35, 0.0), (0.05, 0.70, 2.1), mat_wood_dark)
    add_box("WC_Cua2", (16.98, 1.85, 0.0), (0.05, 0.70, 2.1), mat_wood_dark)

    add_box("Bep_TuongBao", (13.0, 0.0, 0.0), (4.0, 3.0, 3.2), mat_wall)
    add_box("Bep_BanL1", (13.2, 0.2, 0.0), (0.7, 2.6, 0.85), mat_blue_stone)
    add_box("Bep_BanL2", (13.9, 0.2, 0.0), (2.8, 0.7, 0.85), mat_blue_stone)
    add_gabled_roof("Mai_Bep_WC", 12.8, 18.0, 0.0, 3.0, 3.2, 4.1, overhang=0.35, material=mat_roof_red)

    # Nhà Ăn Mái Lá Thôn Quê (4.0m x 10.5m = 42m²) - DẠNG MÁI LÁ Ở QUÊ, CÁC CỘT XONG MÁI LÁ, KHÔNG TƯỜNG
    # Nền gạch Bát Tràng truyền thống có gờ đá xanh
    add_box("NhaAn_Nen_Gach", (13.0, 3.0, 0.02), (4.0, 10.5, 0.08), mat_terracotta_floor)
    add_box("NhaAn_GoDa_Vien", (12.95, 2.95, 0.0), (4.10, 10.60, 0.03), mat_blue_stone)

    # Hệ cột gỗ tròn tự nhiên vững chãi (KHÔNG TƯỜNG - MỞ TOANG 4 BỀ ĐÓN GIÓ)
    # Hàng cột phía đường 8m (X = 13.20) và hàng cột phía dải kỷ vật (X = 16.80)
    cot_y_list = [3.2, 5.7, 8.25, 10.8, 13.3]
    for yp in cot_y_list:
        # Chân tảng đá xanh hoa sen
        add_cylinder(f"ChanTang_CotAn_Trai_{yp}", (13.20, yp, 0.10), 0.16, 0.12, mat_blue_stone)
        add_cylinder(f"Cot_NhaAn_Trai_{yp}",      (13.20, yp, 0.22), 0.11, 2.95, mat_wood_dark)
        add_cylinder(f"ChanTang_CotAn_Phai_{yp}", (16.80, yp, 0.10), 0.16, 0.12, mat_blue_stone)
        add_cylinder(f"Cot_NhaAn_Phai_{yp}",      (16.80, yp, 0.22), 0.11, 2.95, mat_wood_dark)
        # Xà ngang giằng khung vì kèo
        add_box(f"XaNgang_NhaAn_{yp}", (13.20, yp - 0.06, 3.08), (3.60, 0.12, 0.14), mat_wood_dark)

    # Xà dọc giằng mái 2 bên
    add_box("XaDoc_NhaAn_Trai", (13.14, 3.1, 3.10), (0.12, 10.3, 0.14), mat_wood_dark)
    add_box("XaDoc_NhaAn_Phai", (16.74, 3.1, 3.10), (0.12, 10.3, 0.14), mat_wood_dark)

    # Mái lá ở quê (Mái dốc 2 mái rơm rạ / lá cọ dày dặn, độ vươn mái lớn che mưa nắng)
    add_gabled_roof("Mai_NhaAn_MaiLa", 12.6, 17.4, 2.65, 13.85, 3.15, 4.45, overhang=0.45, material=mat_thatch_leaf)
    # Nẹp bờ nóc lá bằng tre bó
    add_box("BoNoc_MaiLa", (14.90, 2.45, 4.45), (0.20, 11.60, 0.16), mat_thatch_ridge)
    for ybn in range(3, 14, 2):
        add_cylinder(f"BoNoc_DayCot_{ybn}", (15.0, ybn, 4.45), 0.12, 0.18, mat_bamboo)

    # Đèn nơm tre dân dã treo thả trần ấm áp
    for y_light, l_idx in [(5.5, 1), (8.25, 2), (11.0, 3)]:
        add_cylinder(f"DayTreo_Den_{l_idx}", (15.0, y_light, 3.5), 0.015, 0.6, mat_wood_dark)
        add_cone(f"DenNomTre_{l_idx}", (15.0, y_light, 2.9), 0.28, 0.45, mat_bamboo)
        add_light_source(f"Den_NhaAn_{l_idx}", (15.0, y_light, 2.7), energy=45.0, color=(1.0, 0.88, 0.70))

    # Bàn ăn tiệc gỗ me tây nguyên tấm dân dã thôn quê
    add_box("BanAn_ThonQue_Than", (14.25, 5.6, 0.0), (1.50, 5.3, 0.72), mat_wood_warm)
    add_box("BanAn_ThonQue_Mat",  (14.10, 5.4, 0.72), (1.80, 5.7, 0.08), mat_wood_dark)
    for ig in range(5):
        add_chair(f"GheAn_Trai_{ig}", (13.55, 5.8 + ig*1.1, 0.0), mat_wood_dark)
        add_chair(f"GheAn_Phai_{ig}", (16.25, 5.8 + ig*1.1, 0.0), mat_wood_dark)
    add_chair("GheAn_Dau1", (15.0, 4.8, 0.0), mat_wood_dark)
    add_chair("GheAn_Dau2", (15.0, 11.6, 0.0), mat_wood_dark)

    # Hành lang kỷ vật xưa (1.0m bên hông)
    add_box("NenSoi_KyVat", (17.02, 3.0, 0.02), (0.96, 10.5, 0.04), mat_pebble)
    for yst in [4.2, 5.8, 7.5, 9.2, 11.0, 12.6]:
        add_cylinder(f"DaBuoc_KyVat_{yst}", (17.5, yst, 0.04), 0.22, 0.03, mat_blue_stone)

    add_light_source("Spot_CoiXay", (17.5, 6.2, 2.5), energy=50.0, color=(1.0, 0.88, 0.70))
    add_light_source("Spot_CoiGia", (17.5, 9.8, 2.5), energy=50.0, color=(1.0, 0.88, 0.70))

    # Cối xay thóc nan tre
    add_cylinder("CoiXay_ThotDuoi", (17.5, 6.2, 0.06), 0.38, 0.42, mat_clay_mill)
    add_cylinder("CoiXay_VanhTre",  (17.5, 6.2, 0.06), 0.40, 0.40, mat_wood_warm)
    add_cylinder("CoiXay_ThotTren", (17.5, 6.2, 0.48), 0.35, 0.35, mat_clay_mill)
    add_box("CoiXay_CanGiang", (17.18, 6.16, 1.05), (0.64, 0.08, 0.08), mat_wood_dark)

    # Rặng trúc quân tử
    for ytr in [7.7, 8.1, 8.5, 8.9]:
        add_cylinder(f"TrucCanh_{ytr}", (17.75, ytr, 0.0), 0.03, 2.6, mat_grass)
        add_cone(f"LaTruc_{ytr}", (17.75, ytr, 2.0), 0.35, 1.0, mat_grass)

    # Cối giã gạo cần đạp chân
    add_cylinder("CoiGia_CoiDa", (17.5, 9.6, 0.06), 0.34, 0.44, mat_blue_stone)
    add_box("CoiGia_CanDap", (17.44, 9.5, 0.40), (0.12, 2.2, 0.12), mat_wood_dark)
    add_cylinder("CoiGia_Chay", (17.5, 9.6, 0.15), 0.07, 0.35, mat_wood_dark)

    # --- KHU 2: NHÀ / CHÒI VUÔNG 4.0m x 4.0m & 2 SÂN THOÁNG (Y = 13.5 -> 25.5m, 12.0m) ---
    # Sân nền tổng Khu 2
    add_box("San_Khu2_Tong", (13.0, 13.5, 0.005), (4.0, 12.0, 0.025), mat_paver_gray)
    
    # Nhà/Chòi Vuông 4m x 4m (X = 13.0 -> 17.0m, Y = 17.5 -> 21.5m)
    xc_v, yc_v = 15.0, 19.5
    # Bệ đá xanh giật cấp hình vuông 4m
    add_box("De_ChoiVuong_Cap1", (12.9, 17.4, 0.0),  (4.2, 4.2, 0.20), mat_blue_stone)
    add_box("De_ChoiVuong_Cap2", (13.0, 17.5, 0.20), (4.0, 4.0, 0.20), mat_blue_stone)
    add_box("San_Go_ChoiVuong",  (13.1, 17.6, 0.40), (3.8, 3.8, 0.06), mat_wood_dark)

    # 4 Cột gỗ lim 4 góc chòi vuông
    col_coords = [
        (13.4, 17.9), (16.6, 17.9),
        (13.4, 21.1), (16.6, 21.1)
    ]
    for ic, (px, py) in enumerate(col_coords):
        add_cylinder(f"ChanTang_ChoiVuong_{ic}", (px, py, 0.40), 0.18, 0.15, mat_blue_stone)
        add_cylinder(f"Cot_ChoiVuong_{ic}", (px, py, 0.55), 0.14, 2.85, mat_wood_dark)

    # Lan can gỗ 3 mặt (chừa mặt trước hướng ra đường 8m)
    add_box("LanCan_Sau",  (16.55, 17.9, 0.46), (0.08, 3.2, 0.65), mat_wood_warm)
    add_box("LanCan_Nam",  (13.4, 17.85, 0.46), (3.2, 0.08, 0.65), mat_wood_warm)
    add_box("LanCan_Bac",  (13.4, 21.05, 0.46), (3.2, 0.08, 0.65), mat_wood_warm)

    # Bàn trà vuông thưởng ngoạn ở giữa
    add_box("BanTra_ChoiVuong", (14.5, 19.0, 0.46), (1.0, 1.0, 0.75), mat_wood_dark)
    for idn, (dx, dy) in enumerate([(-0.8, 0.0), (0.8, 0.0), (0.0, -0.8), (0.0, 0.8)]):
        add_cylinder(f"DonGhe_Vuong_{idn}", (xc_v + dx, yc_v + dy, 0.46), 0.20, 0.45, mat_wood_warm)

    # Mái ngói đỏ 4 mái hình chóp chồng diêm cho chòi vuông
    add_pyramid_roof("MaiChoi_Tang1", 12.8, 17.2, 17.3, 21.7, 3.4, 4.35, overhang=0.4, material=mat_roof_red)
    add_box("CoDiem_Vuong", (14.2, 18.7, 4.35), (1.6, 1.6, 0.45), mat_wood_dark)
    add_pyramid_roof("MaiChoi_Tang2", 13.6, 16.4, 18.1, 20.9, 4.8, 5.85, overhang=0.3, material=mat_roof_red)
    add_cylinder("HoLo_De",  (xc_v, yc_v, 5.85), 0.18, 0.15, mat_gold)
    add_cone("HoLo_Dinh",    (xc_v, yc_v, 6.00), 0.14, 0.45, mat_gold)

    # --- KHU 1: NHÀ 3 GIAN BẮC BỘ TRUYỀN THỐNG (Y = 25.5 -> 37.0m, Dài 11.5m) ---
    # Rút gọn bề ngang còn 4.0m (X = 13.0 -> 17.0m)
    add_box("TamCap_Nha3Gian",  (12.5, 27.0, 0.0), (0.5, 6.0, 0.22), mat_blue_stone)
    add_box("He_Nha3Gian",      (13.0, 25.5, 0.0), (0.9, 9.0, 0.45), mat_blue_stone)
    add_box("San_Nha3Gian",     (13.9, 25.5, 0.0), (3.1, 9.0, 0.45), mat_paver_gray)
    add_box("San_GachBatTrang", (13.92, 25.52, 0.45), (3.04, 8.94, 0.02), mat_terracotta_floor)

    # 4 Cột hiên gỗ lim bệ đá hoa sen
    for yh in [25.8, 28.8, 31.8, 34.2]:
        add_cylinder(f"ChanTang_Hien_{yh}", (13.45, yh, 0.45), 0.16, 0.15, mat_blue_stone)
        add_cylinder(f"CotHien_Nha3Gian_{yh}", (13.45, yh, 0.60), 0.12, 2.85, mat_wood_dark)
    add_box("XaHien_Nha3Gian", (13.40, 25.5, 3.35), (0.12, 9.0, 0.15), mat_wood_dark)

    # Tường hồi Nam, Bắc và tường hậu
    add_box("TuongHoi_Nam_Nha3Gian", (13.9, 25.5, 0.0), (3.1, 0.22, 3.6), mat_wall)
    add_box("TuongHoi_Bac_Nha3Gian", (13.9, 34.28, 0.0), (3.1, 0.22, 3.6), mat_wall)
    add_box("TuongHau_Nha3Gian",     (16.78, 25.5, 0.0), (0.22, 9.0, 3.6), mat_wall)

    # Vách mặt tiền & hệ cửa bức bàn 3 gian (tại X = 13.9)
    add_box("NguongCua_Nha3Gian",    (13.86, 25.5, 0.45), (0.10, 9.0, 0.12), mat_wood_dark)
    add_box("KhungCua_Dinh_Nha3Gian", (13.86, 25.5, 3.10), (0.10, 9.0, 0.12), mat_wood_dark)

    # 1. Cửa bức bàn Gian Tả (Y = 25.8 -> 28.2)
    add_door_panel("CanhCua_Ta_1", (13.90, 26.15, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=45.0, mat_panel=mat_wood_dark)
    add_door_panel("CanhCua_Ta_2", (13.90, 27.85, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=-45.0, mat_panel=mat_wood_dark)

    # 2. Cửa bức bàn Gian Giữa (Y = 28.8 -> 31.2) - Mở rộng thênh thang
    add_door_panel("CanhCua_Giua_1", (13.90, 29.15, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=65.0, mat_panel=mat_wood_dark)
    add_door_panel("CanhCua_Giua_2", (13.90, 30.85, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=-65.0, mat_panel=mat_wood_dark)

    # 3. Cửa bức bàn Gian Hữu (Y = 31.8 -> 34.2)
    add_door_panel("CanhCua_Huu_1", (13.90, 32.15, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=45.0, mat_panel=mat_wood_dark)
    add_door_panel("CanhCua_Huu_2", (13.90, 33.85, 0.57), width=0.85, thickness=0.035, height=2.45, angle_deg=-45.0, mat_panel=mat_wood_dark)

    add_box("Mai_VachTien_Nha3Gian", (13.86, 25.5, 3.22), (0.10, 9.0, 0.38), mat_wall)

    # Cột cái & cột hậu bên trong nhà
    for yc in [28.5, 31.5]:
        add_cylinder(f"ChanTang_CotCai_{yc}", (15.2, yc, 0.47), 0.18, 0.15, mat_blue_stone)
        add_cylinder(f"CotCai_Nha3Gian_{yc}", (15.2, yc, 0.62), 0.14, 3.65, mat_wood_dark)
        add_cylinder(f"ChanTang_CotHau_{yc}", (16.5, yc, 0.47), 0.16, 0.15, mat_blue_stone)
        add_cylinder(f"CotHau_Nha3Gian_{yc}", (16.5, yc, 0.62), 0.12, 3.00, mat_wood_dark)

    add_box("CauDau_GianGiua", (15.12, 28.5, 3.45), (0.16, 3.0, 0.20), mat_wood_dark)

    # Gian Giữa Thờ Tổ: Án gian thếp vàng, đồ thờ ngũ sự
    add_box("AnGian_ChanDe",   (15.40, 29.20, 0.47), (1.30, 1.60, 0.25), mat_wood_dark)
    add_box("AnGian_DaTien",   (15.38, 29.18, 0.72), (1.34, 1.64, 0.45), mat_lacquer_red)
    add_box("AnGian_ChamRong", (15.36, 29.25, 0.75), (0.04, 1.50, 0.40), mat_gold)
    add_box("AnGian_MatBan",   (15.30, 29.10, 1.68), (1.45, 1.80, 0.06), mat_wood_dark)

    add_box("AnGian_Cap2_Than", (16.10, 29.45, 1.74), (0.60, 1.10, 0.35), mat_lacquer_red)
    add_box("AnGian_Cap2_Mat",  (16.05, 29.40, 2.09), (0.68, 1.20, 0.04), mat_gold)
    add_box("NgaiTho_De",       (16.25, 29.75, 2.13), (0.42, 0.50, 0.15), mat_gold)
    add_box("BaiVi_ToTien",     (16.45, 29.90, 2.28), (0.04, 0.20, 0.42), mat_gold)

    # Ngũ sự đồng
    add_cylinder("LuDong_De",  (15.70, 30.00, 1.74), 0.14, 0.10, mat_bronze)
    add_cylinder("LuDong_Than",(15.70, 30.00, 1.84), 0.17, 0.25, mat_gold)
    add_cylinder("Rua_Trai", (15.70, 29.65, 1.74), 0.10, 0.07, mat_bronze)
    add_cylinder("Hac_Trai", (15.70, 29.65, 1.81), 0.02, 0.38, mat_gold)
    add_cylinder("Rua_Phai", (15.70, 30.35, 1.74), 0.10, 0.07, mat_bronze)
    add_cylinder("Hac_Phai", (15.70, 30.35, 1.81), 0.02, 0.38, mat_gold)
    add_cylinder("BatHuong_Lam", (15.46, 30.00, 1.74), 0.11, 0.17, mat_tea_pot)

    # Hoành phi & Câu đối
    add_box("HoanhPhi_Khung", (16.74, 29.10, 2.85), (0.04, 1.80, 0.65), mat_lacquer_red)
    add_box("HoanhPhi_Vang",  (16.73, 29.25, 2.95), (0.02, 1.50, 0.45), mat_gold)
    add_box("CauDoi_CotTrai", (15.18, 28.46, 1.15), (0.06, 0.16, 2.20), mat_lacquer_red)
    add_box("CauDoi_CotPhai", (15.18, 31.46, 1.15), (0.06, 0.16, 2.20), mat_lacquer_red)

    # Đôi Lục Bình
    for ylb, nlb in [(28.75, "Trai"), (31.25, "Phai")]:
        add_cylinder(f"LucBinh_{nlb}_De",   (16.00, ylb, 0.47), 0.16, 0.20, mat_wood_dark)
        add_cylinder(f"LucBinh_{nlb}_Than", (16.00, ylb, 0.67), 0.20, 0.85, mat_wood_dark)
        add_cone(f"LucBinh_{nlb}_Co",       (16.00, ylb, 1.52), 0.11, 0.35, mat_wood_dark)

    add_box("ChieuCoi_GianGiua", (14.20, 29.00, 0.47), (1.10, 2.00, 0.015), mat_mat_rush)

    # Gian Tả: Trường kỷ & Tủ chè
    add_box("TruongKy_Ghe1", (14.20, 26.00, 0.47), (0.55, 1.80, 0.42), mat_wood_dark)
    add_box("TruongKy_Ghe2", (15.60, 26.00, 0.47), (0.55, 1.80, 0.42), mat_wood_dark)
    add_box("TruongKy_Ban",  (14.85, 26.00, 0.47), (0.50, 1.80, 0.72), mat_wood_dark)
    add_box("TuChe_Than",    (16.15, 26.00, 0.47), (0.58, 1.80, 0.88), mat_wood_dark)

    # Gian Hữu: Sập gụ & Tủ gia phả
    add_box("SapGu_ChanDe", (14.10, 32.00, 0.47), (1.50, 1.90, 0.28), mat_wood_dark)
    add_box("SapGu_MatSap", (14.05, 31.95, 0.75), (1.60, 2.00, 0.08), mat_wood_warm)
    add_box("SapGu_Goi1",   (14.25, 32.15, 0.83), (0.40, 0.20, 0.22), mat_cushion_red)
    add_box("TuGiaPha_Duoi",(16.15, 32.00, 0.47), (0.58, 1.90, 0.75), mat_wood_dark)

    # Đèn lồng & chiếu sáng
    add_cylinder("DenLong_GianGiua", (15.2, 30.0, 3.25), 0.22, 0.40, mat_gold, vertices=6)
    add_light_source("Light_GianGiua", (15.2, 30.0, 3.05), energy=60.0, color=(1.0, 0.88, 0.65))

    add_gabled_roof("Mai_Nha3Gian", 13.0, 17.5, 25.2, 34.8, 3.45, 4.75, overhang=0.4, material=mat_roof_red)
    add_box("BoNoc_Nha3Gian", (15.25, 25.0, 4.75), (0.22, 10.0, 0.18), mat_blue_stone)
    add_cone("KimNoc_Dau", (15.36, 25.0, 4.93), 0.14, 0.38, mat_gold)
    add_cone("KimNoc_Cuoi", (15.36, 35.0, 4.93), 0.14, 0.38, mat_gold)

    # Phụ trợ sau nhà: Vườn hồng, chuối, toilet & đường 1m
    add_box("VuonHong_Khu1", (13.2, 34.7, 0.05), (1.6, 1.1, 0.15), mat_grass)
    add_cylinder("BuiChuoi_1", (15.0, 35.3, 0.0), 0.12, 2.0, mat_grass)
    add_box("Toilet_SauNha3Gian", (15.2, 34.5, 0.0), (1.8, 1.5, 2.6), mat_wall)
    add_gabled_roof("Mai_Toilet_Sau", 15.0, 17.1, 34.4, 36.1, 2.6, 3.1, overhang=0.2, material=mat_roof_red)
    add_box("DuongDi1m_Khu1", (13.0, 36.0, 0.01), (5.0, 1.0, 0.04), mat_blue_stone)

    # =========================================================================
    # 6. DÃY BÊN TRÁI (X = 0.0 -> 5.0m, Rộng 5.0m, Dài 37.0m)
    # BỐ TRÍ MỚI THEO YÊU CẦU:
    # 1. Căn Nhà 1 (6x4): Y = 0.0 -> 6.0m
    # 2. Căn Nhà 2 (6x4): Y = 6.0 -> 12.0m (liền kề Căn 1)
    # 3. Cái Ao Cá Quê: Y = 12.0 -> 17.0m (dài 5.0m)
    # 4. Căn Nhà 3 (6x4): Y = 17.0 -> 23.0m
    # 5. Cái Vườn Cây: Y = 23.0 -> 37.0m (dài 14.0m)
    # =========================================================================
    add_box("DaiLui_Trai_1m", (0.0, 0.0, 0.005), (1.0, 37.0, 0.02), mat_paver_gray)

    # HÀM TẠO 1 CĂN NHÀ NGHỈ DƯỠNG GIA TỘC 6x4 (Rộng 4m, Dài 6m)
    def add_house_6x4(prefix, y_start, room_type="master"):
        # Sàn gỗ & tường bao
        add_box(f"{prefix}_San", (1.0, y_start, 0.01), (4.0, 6.0, 0.06), mat_wood_floor)
        add_box(f"{prefix}_TuongTrai", (1.0, y_start, 0.0), (0.18, 6.0, 3.2), mat_wall)
        add_box(f"{prefix}_TuongDau",  (1.0, y_start, 0.0), (4.0, 0.18, 3.2), mat_wall)
        add_box(f"{prefix}_TuongCuoi", (1.0, y_start + 5.82, 0.0), (4.0, 0.18, 3.2), mat_wall)
        
        # Tường mặt tiền giáp đường 8m (X = 4.82 -> 5.0m)
        add_box(f"{prefix}_TuongPhai_Thap",    (4.82, y_start, 0.0), (0.18, 6.0, 0.8), mat_wall)
        add_box(f"Mai_{prefix}_TuongPhai_Cao", (4.82, y_start, 0.8), (0.18, 6.0, 2.4), mat_wall)
        
        # Cửa ra vào & cửa sổ
        add_box(f"{prefix}_KhungCua", (4.78, y_start + 1.0, 0.0), (0.06, 1.20, 2.20), mat_wood_dark)
        add_box(f"{prefix}_Cua",      (4.80, y_start + 1.05, 0.02), (0.04, 1.10, 2.15), mat_wood_dark)
        add_box(f"{prefix}_CuaSoKinh", (4.80, y_start + 3.0, 1.0), (0.04, 2.0, 1.5), mat_glass)

        # Phòng tắm WC khép kín (Góc tựa tường rào 1m: X = 1.18 -> 2.68, Y = y_start + 0.18 -> y_start + 1.88)
        add_box(f"{prefix}_WC_TuongDoc",   (2.68, y_start + 0.18, 0.0), (0.10, 1.70, 2.6), mat_wall)
        add_box(f"{prefix}_WC_TuongNgang", (1.18, y_start + 1.88, 0.0), (1.60, 0.10, 2.6), mat_wall)
        add_box(f"{prefix}_WC_Cua",        (1.88, y_start + 1.86, 0.0), (0.75, 0.04, 2.1), mat_wood_dark)
        add_box(f"{prefix}_WC_San",        (1.18, y_start + 0.18, 0.02), (1.50, 1.70, 0.04), mat_slate_wc)
        add_box(f"{prefix}_WC_Lavabo",     (2.10, y_start + 0.30, 0.05), (0.50, 0.45, 0.82), mat_black_marble)
        add_cylinder(f"{prefix}_WC_Chau",  (2.35, y_start + 0.52, 0.85), 0.15, 0.10, mat_ceramic_wc)
        add_box(f"{prefix}_WC_Toilet",     (2.10, y_start + 1.20, 0.05), (0.45, 0.55, 0.45), mat_ceramic_wc)

        # Giường ngủ & nội thất
        if room_type == "master":
            # Giường King-size
            add_box(f"{prefix}_Giuong_Khung", (1.80, y_start + 2.60, 0.05), (1.90, 2.10, 0.40), mat_wood_warm)
            add_box(f"{prefix}_Giuong_Nem",   (1.88, y_start + 2.68, 0.45), (1.74, 1.94, 0.22), mat_white_linen)
            add_box(f"{prefix}_Giuong_Goi1",  (2.05, y_start + 2.75, 0.67), (0.55, 0.38, 0.10), mat_pillow)
            add_box(f"{prefix}_Giuong_Goi2",  (2.85, y_start + 2.75, 0.67), (0.55, 0.38, 0.10), mat_pillow)
        elif room_type == "twin":
            # 2 Giường đơn Twin beds
            add_box(f"{prefix}_GiuongA_Khung", (1.30, y_start + 2.60, 0.05), (1.10, 2.00, 0.40), mat_wood_warm)
            add_box(f"{prefix}_GiuongA_Nem",   (1.35, y_start + 2.65, 0.45), (1.00, 1.90, 0.22), mat_white_linen)
            add_box(f"{prefix}_GiuongB_Khung", (2.65, y_start + 2.60, 0.05), (1.10, 2.00, 0.40), mat_wood_warm)
            add_box(f"{prefix}_GiuongB_Nem",   (2.70, y_start + 2.65, 0.45), (1.00, 1.90, 0.22), mat_white_linen)
        else: # view ao & vườn
            # Giường Queen & Bàn trà ngắm cảnh
            add_box(f"{prefix}_Giuong_Khung", (1.50, y_start + 2.80, 0.05), (1.80, 2.00, 0.40), mat_wood_warm)
            add_box(f"{prefix}_Giuong_Nem",   (1.55, y_start + 2.85, 0.45), (1.70, 1.90, 0.22), mat_white_linen)
            add_box(f"{prefix}_BanTraView",   (3.60, y_start + 2.20, 0.05), (0.80, 1.20, 0.45), mat_wood_dark)

        # Tủ áo & Đèn phòng
        add_box(f"{prefix}_TuAo", (1.18, y_start + 4.70, 0.05), (1.20, 0.55, 2.30), mat_wood_dark)
        add_light_source(f"Light_{prefix}", (3.0, y_start + 3.0, 2.5), energy=30.0, color=(1.0, 0.92, 0.82))

        # Mái ngói đỏ Bát Tràng
        add_gabled_roof(f"Mai_{prefix}", 0.8, 5.2, y_start, y_start + 6.0, 3.2, 4.35, overhang=0.35, material=mat_roof_red)

    # 1. CĂN NHÀ 1 (6x4): Y = 0.0 -> 6.0m
    add_house_6x4("NhaKhach1_6x4", 0.0, room_type="master")

    # 2. CĂN NHÀ 2 (6x4): Y = 6.0 -> 12.0m (Liền kề Căn 1)
    add_house_6x4("NhaKhach2_6x4", 6.0, room_type="twin")

    # 3. CÁI AO CÁ QUÊ (Y = 12.0 -> 17.0m, Dài 5.0m x Rộng 4.5m)
    # Lòng ao rỗng sâu -0.70m, nước trong, đá kè, đàn cá bơi lội, cầu ao
    add_box("DayAo_SanDatCat", (0.8, 12.15, -0.70), (4.0, 4.7, 0.05), mat_pond_bottom)
    add_box("ThanhAo_Nam",     (0.8, 12.00, -0.70), (4.0, 0.15, 0.70), mat_pond_wall)
    add_box("ThanhAo_Bac",     (0.8, 16.85, -0.70), (4.0, 0.15, 0.70), mat_pond_wall)
    add_box("ThanhAo_Tay",     (0.65, 12.00, -0.70), (0.15, 5.0, 0.70), mat_pond_wall)
    add_box("ThanhAo_Dong",    (4.85, 12.00, -0.70), (0.15, 5.0, 0.70), mat_pond_wall)

    # Kè đá cuội tự nhiên quanh ao
    for ix in range(7):
        rx = 1.0 + ix * 0.60
        add_sphere(f"DaBoAo_Nam_{ix}", (rx, 12.06, -0.04), radius=0.20, scale=(1.2, 0.9, 0.65), material=mat_rock_river)
        add_sphere(f"DaBoAo_Bac_{ix}", (rx, 16.94, -0.04), radius=0.22, scale=(1.1, 0.8, 0.70), material=mat_rock_river)
    for iy in range(7):
        ry = 12.5 + iy * 0.65
        add_sphere(f"DaBoAo_Tay_{iy}", (0.75, ry, -0.04), radius=0.22, scale=(0.8, 1.2, 0.65), material=mat_rock_river)
        add_sphere(f"DaBoAo_Dong_{iy}", (4.86, ry, -0.04), radius=0.22, scale=(0.85, 1.1, 0.65), material=mat_rock_river)

    # Mặt nước ao cá (Cao độ Z = -0.10m)
    add_box("MatNuoc_AoCa_TrongSuot", (0.82, 12.16, -0.10), (3.98, 4.68, 0.04), mat_water)

    # Đàn cá chép đồng bơi lội
    carp_data = [
        ("CaChep_Bac1",    (2.4, 13.0, -0.14), 55.0,   0.85, mat_carp_silver, mat_carp_fin),
        ("CaChep_VangDong",(3.4, 13.4, -0.13), -40.0,  0.90, mat_carp_gold,   mat_carp_fin),
        ("CaChep_Bac2",    (2.8, 14.2, -0.15), 125.0,  0.80, mat_carp_silver, mat_carp_fin),
        ("CaChep_DoQue1",  (4.0, 14.0, -0.14), -75.0,  0.75, mat_carp_red,    mat_carp_fin),
        ("CaChep_Dong3",   (1.8, 14.5, -0.15), 15.0,   0.82, mat_carp_silver, mat_carp_fin),
        ("CaChep_Vang2",   (3.5, 15.0, -0.14), -120.0, 0.85, mat_carp_gold,   mat_carp_fin),
        ("CaChep_DoQue2",  (2.6, 15.4, -0.15), 85.0,   0.78, mat_carp_red,    mat_carp_fin),
    ]
    for c_name, c_loc, c_yaw, c_sc, c_mb, c_mf in carp_data:
        add_carp_fish(c_name, c_loc, c_yaw, c_sc, c_mb, c_mf)

    add_light_source("Light_AoCa_Fill", (2.8, 14.2, 0.20), energy=35.0, color=(0.92, 0.98, 0.95))

    # Cụm hoa sen & hoa súng
    lotus_clusters = [
        ("Sen_Cum1", (1.4, 13.2, -0.09)),
        ("Sen_Cum2", (4.2, 15.8, -0.09)),
        ("Sen_Cum3", (1.5, 15.6, -0.09))
    ]
    for c_name, c_pos in lotus_clusters:
        add_lotus_cluster(c_name, c_pos, mat_lotus_leaf, mat_lotus_pink, mat_lotus_yellow)

    # =========================================================================
    # CẦU AO ĐỂ ĐI LÊN NGẮM CẢNH & CHỖ GIẶT ĐỒ Ở CẦU AO NHƯ Ở QUÊ NGÀY XƯA
    # =========================================================================
    # 1. BẬC BƯỚC XUỐNG CẦU AO TỪ ĐẠI LỘ 8M
    add_box("TamCap_CauAo_1", (4.70, 13.5, 0.02), (0.28, 1.60, 0.06), mat_blue_stone)
    add_box("TamCap_CauAo_2", (4.45, 13.5, -0.02), (0.25, 1.60, 0.06), mat_blue_stone)

    # 2. SÀN CẦU AO GỖ LIM VƯƠN RA LÒNG AO ĐỂ ĐI LÊN NGẮM CẢNH
    # Sàn vươn từ X = 2.40 -> 4.45 (dài hơn 2m ra mặt nước), rộng Y = 13.6 -> 15.1
    add_box("San_CauAo_GoLim", (2.40, 13.6, 0.01), (2.05, 1.50, 0.06), mat_wood_deck)
    # Các cọc trụ gỗ lim đóng xuống lòng ao đỡ sàn
    for (px, py) in [(2.50, 13.70), (2.50, 15.00), (3.50, 13.70), (3.50, 15.00), (4.40, 13.70), (4.40, 15.00)]:
        add_cylinder(f"CocTru_CauAo_{px}_{py}", (px, py, -0.68), 0.06, 0.75, mat_wood_dark)

    # Lan can tay vịn tre / gỗ lim mộc mạc phía bắc cầu ao để vịn ngắm cá
    add_cylinder("CocLanCan_1", (2.50, 15.05, 0.05), 0.04, 0.85, mat_bamboo)
    add_cylinder("CocLanCan_2", (3.50, 15.05, 0.05), 0.04, 0.85, mat_bamboo)
    add_cylinder("CocLanCan_3", (4.45, 15.05, 0.05), 0.04, 0.85, mat_bamboo)
    add_box("TayVin_CauAo", (2.45, 15.02, 0.85), (2.05, 0.06, 0.06), mat_bamboo)

    # 3. CHỖ GIẶT ĐỒ Ở CẦU AO NHƯ Ở QUÊ NGÀY XƯA
    # Bậc đá hạ thấp sát mấp mé mặt nước (Z = -0.05m, nước Z = -0.10m)
    add_box("BacBen_DaXanh_Giat", (3.20, 12.60, -0.06), (1.20, 0.95, 0.06), mat_blue_stone)
    
    # Phiến đá giặt đồ (bàn đập giặt xưa) phẳng lì nhẵn bóng nằm sát mép nước
    add_box("PhienDa_GiatDo", (2.55, 12.65, -0.05), (0.65, 0.85, 0.06), mat_wash_stone)

    # Chiếc thau đồng / chậu giặt cổ truyền đặt trên phiến đá
    add_cylinder("ThauDong_GiatDo_Day", (2.85, 12.95, 0.01), 0.22, 0.02, mat_wash_tub)
    add_cylinder("ThauDong_GiatDo_Vanh", (2.85, 12.95, 0.03), 0.24, 0.12, mat_wash_tub, vertices=16)

    # Chiếc chày gỗ đập giặt đồ cổ truyền
    add_cylinder("ChayDap_GiatDo", (2.70, 13.30, 0.02), 0.03, 0.35, mat_wood_dark)

    # Cọc tre cắm lòng ao cạnh phiến đá để vịn tay khi giặt giũ
    add_cylinder("CocTre_VinTay_Giat", (2.45, 12.65, -0.68), 0.04, 1.45, mat_bamboo)
    # Khăn vải chàm / quần áo vắt trên cọc phơi
    add_box("VaiCham_Phoi_Giat", (2.42, 12.62, 0.60), (0.06, 0.16, 0.25), mat_cotton_cloth)

    # 4. CĂN NHÀ 3 (6x4): Y = 17.0 -> 23.0m (Nằm sau ao, trước vườn)
    add_house_6x4("NhaKhach3_6x4", 17.0, room_type="view_ao_vuon")

    # 5. CÁI VƯỜN CÂY XANH MÁT (Y = 23.0 -> 37.0m, Dài 14.0m x Rộng 5.0m = 70 m²)
    add_box("ThamCo_VuonKhu6", (0.0, 23.0, 0.01), (5.0, 14.0, 0.03), mat_grass)
    path_points = [
        (3.5, 23.8), (3.0, 25.5), (3.8, 27.2), (2.8, 29.0),
        (3.2, 31.0), (2.5, 33.2), (3.4, 35.5)
    ]
    for idx, (px, py) in enumerate(path_points):
        add_cylinder(f"DaBuocDao_{idx}", (px, py, 0.03), 0.38, 0.04, mat_blue_stone)

    trees_data = [
        ("CayBuoi_1",    (1.8, 24.8, 0.0), 0.22, 3.6, 1.7),
        ("CayMocHuong",  (4.0, 27.0, 0.0), 0.18, 3.2, 1.5),
        ("CayKheNgot",   (1.6, 29.5, 0.0), 0.24, 3.8, 1.9),
        ("CayMaiVang",   (3.8, 32.5, 0.0), 0.16, 3.0, 1.4),
        ("CayBuoi_2",    (2.0, 35.0, 0.0), 0.20, 3.4, 1.6),
    ]
    for t_name, loc, tr, h, fr in trees_data:
        add_tree(t_name, loc, tr, h, fr, mat_wood_dark, mat_grass)

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
    # 8. THIẾT LẬP 12 GÓC CAMERA PHỐI CẢNH
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
    setup_camera("Cam_2_BocMai", (22.0, -5.0, 25.0), (9.0, 16.5, 1.0), focal_length=30)

    # 3. Cận cảnh Chòi Vuông 4m x 4m & Nhà 3 Gian Bắc Bộ
    setup_camera("Cam_3_DaiLucGiac_Nha3Gian", (5.0, 16.0, 7.0), (15.0, 24.0, 2.5), focal_length=30)

    # 4. Hành lang kỷ vật xưa & Bàn ăn qua vách kính
    setup_camera("Cam_4_KyVat_NhaAn", (14.2, 4.0, 1.6), (17.4, 8.0, 1.0), focal_length=28)

    # 5. Cận cảnh Ao Cá Quê nhìn từ hiên Căn Nhà 2
    setup_camera("Cam_5_ViewAo_PhongNgam", (3.0, 10.5, 1.4), (3.0, 14.5, 0.10), focal_length=22)

    # 6. Phối cảnh cổng chính mở rộng 8m nhìn sâu vào trục đại lộ
    setup_camera("Cam_6_CongChinh", (9.0, -8.5, 1.8), (9.0, 16.0, 1.6), focal_length=28)

    # 7. Cận cảnh 2 Căn Nhà 6x4 và Ao Cá Dãy Trái
    setup_camera("Cam_7_HanhLang_NhaKhach", (5.5, 0.8, 1.8), (3.0, 12.0, 1.2), focal_length=24)

    # 8. Cận cảnh nội thất Nhà 3 Gian Bắc Bộ
    setup_camera("Cam_8_NoiThat_Nha3Gian", (12.5, 30.0, 1.55), (15.5, 30.0, 1.65), focal_length=18)

    # 9. PHỐI CẢNH HƯỚNG NAM (Từ cổng chính vào toàn bộ khuôn viên)
    setup_camera("Cam_Huong_Nam", (9.0, -15.0, 13.0), (9.0, 18.5, 2.0), focal_length=28)

    # 10. PHỐI CẢNH HƯỚNG BẮC (Từ cuối khu đất nhìn về cổng)
    setup_camera("Cam_Huong_Bac", (9.0, 52.0, 14.0), (9.0, 18.5, 2.0), focal_length=28)

    # 11. PHỐI CẢNH HƯỚNG ĐÔNG (Nhìn sang Dãy Trái: 3 Nhà 6x4, Ao cá, Vườn 14m)
    setup_camera("Cam_Huong_Dong", (34.0, 18.5, 14.0), (9.0, 18.5, 2.0), focal_length=28)

    # 12. PHỐI CẢNH HƯỚNG TÂY (Nhìn sang Dãy Phải: Bếp, Nhà Ăn, Chòi Vuông 4m, Nhà 3 Gian)
    setup_camera("Cam_Huong_Tay", (-16.0, 18.5, 14.0), (9.0, 18.5, 2.0), focal_length=28)

    blend_path = "d:/Work/Khu_Nha_Dong_Ho/khu_nha_dong_ho.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f">>> [BLENDER] Đã lưu thành công tệp dự án mới: {blend_path}")

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
