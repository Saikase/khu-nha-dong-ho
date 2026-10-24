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

def add_mini_tree(name, location, trunk_r=0.05, height=1.6, foliage_r=0.5, wood_mat=None, leaf_mat=None):
    """Cây cảnh nhỏ / cau kiểng / bụi hoa thanh mảnh làm duyên"""
    lx, ly, lz = location
    add_cylinder(f"{name}_than", (lx, ly, lz), trunk_r, height * 0.45, wood_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=foliage_r, location=(lx, ly, lz + height * 0.75))
    fol = bpy.context.active_object
    fol.name = f"{name}_tan"
    fol.scale = (0.9, 0.9, 1.25)
    bpy.ops.object.shade_smooth()
    if leaf_mat:
        fol.data.materials.append(leaf_mat)

def add_slanted_glass_roof(name, x1, z1, x2, z2, y_min, y_max, thickness=0.015, material=None):
    """Tạo mái kính nghiêng nối từ mép mái xuống đỉnh tường rào để lấy sáng rọi kỷ vật"""
    dx = x2 - x1
    dz = z2 - z1
    length = math.sqrt(dx*dx + dz*dz)
    nx = -dz / length * thickness
    nz = dx / length * thickness
    
    verts = [
        (x1, y_min, z1),
        (x2, y_min, z2),
        (x2, y_max, z2),
        (x1, y_max, z1),
        (x1 + nx, y_min, z1 + nz),
        (x2 + nx, y_min, z2 + nz),
        (x2 + nx, y_max, z2 + nz),
        (x1 + nx, y_max, z1 + nz),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

def add_areca_palm(name, location, height=4.0, mat_trunk=None, mat_frond=None, mat_fruit=None):
    """Cây cau ta truyền thống Bắc Bộ: thân thon thẳng đứng, ngấn đốt cau, bẹ lá xòe, buồng cau buông rủ"""
    lx, ly, lz = location
    trunk_h = height * 0.78
    add_cylinder(f"{name}_than", (lx, ly, lz), 0.065, trunk_h, mat_trunk)
    num_rings = int(trunk_h / 0.28)
    for ir in range(1, num_rings):
        rz = lz + ir * 0.28
        add_cylinder(f"{name}_ngan_{ir}", (lx, ly, rz), 0.072, 0.02, mat_trunk)
    add_cylinder(f"{name}_be_xanh", (lx, ly, lz + trunk_h), 0.060, height * 0.12, mat_frond)
    if mat_fruit:
        add_sphere(f"{name}_buong_cau", (lx + 0.12, ly + 0.05, lz + trunk_h + 0.08), radius=0.14, scale=(0.8, 0.8, 1.4), material=mat_fruit)
    top_z = lz + trunk_h + height * 0.10
    num_fronds = 6
    for ifr in range(num_fronds):
        ang = math.radians(ifr * (360 / num_fronds) + 20)
        fx = lx + 0.55 * math.cos(ang)
        fy = ly + 0.55 * math.sin(ang)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.015, depth=1.3, location=(fx, fy, top_z + 0.22))
        frond_stem = bpy.context.active_object
        frond_stem.name = f"{name}_frond_{ifr}"
        pitch = math.radians(45)
        frond_stem.rotation_euler = (pitch * math.sin(ang), -pitch * math.cos(ang), ang)
        if mat_frond:
            frond_stem.data.materials.append(mat_frond)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.26, depth=1.1, location=(fx * 1.3 - lx * 0.3, fy * 1.3 - ly * 0.3, top_z + 0.10))
        frond_leaf = bpy.context.active_object
        frond_leaf.name = f"{name}_leaf_{ifr}"
        frond_leaf.scale = (0.2, 1.0, 0.6)
        frond_leaf.rotation_euler = (pitch * 1.2 * math.sin(ang), -pitch * 1.2 * math.cos(ang), ang)
        if mat_frond:
            frond_leaf.data.materials.append(mat_frond)

def add_grapefruit_tree(name, location, trunk_r=0.14, height=3.2, mat_wood=None, mat_leaf=None, mat_fruit=None):
    """Cây bưởi Diễn / bưởi cảnh trĩu quả tròn vàng óng"""
    lx, ly, lz = location
    add_cylinder(f"{name}_than", (lx, ly, lz), trunk_r, height * 0.42, mat_wood)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.35, location=(lx, ly, lz + height * 0.72))
    fol = bpy.context.active_object
    fol.name = f"{name}_tan"
    bpy.ops.object.shade_smooth()
    if mat_leaf:
        fol.data.materials.append(mat_leaf)
    fruit_locs = [
        (0.65, 0.35, 1.8), (-0.55, 0.45, 1.7), (0.30, -0.70, 1.6),
        (-0.40, -0.50, 1.85), (0.75, -0.25, 2.0), (0.10, 0.75, 1.9)
    ]
    for ifr, (dx, dy, fz) in enumerate(fruit_locs):
        add_sphere(f"{name}_qua_{ifr}", (lx + dx, ly + dy, lz + fz), radius=0.11, material=mat_fruit)

def add_loc_vung_tree(name, location, trunk_r=0.15, height=3.4, mat_wood=None, mat_leaf=None, mat_flower=None):
    """Cây lộc vừng dáng uốn lượn phong thủy, chuỗi hoa đỏ thắm buông rủ"""
    lx, ly, lz = location
    add_cylinder(f"{name}_than1", (lx, ly, lz), trunk_r, height * 0.30, mat_wood)
    add_cylinder(f"{name}_than2", (lx + 0.15, ly + 0.10, lz + height * 0.25), trunk_r * 0.85, height * 0.30, mat_wood)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.45, location=(lx + 0.10, ly + 0.05, lz + height * 0.75))
    fol = bpy.context.active_object
    fol.name = f"{name}_tan"
    bpy.ops.object.shade_smooth()
    if mat_leaf:
        fol.data.materials.append(mat_leaf)
    flower_locs = [
        (0.70, 0.30, 2.0), (-0.60, 0.40, 1.9), (0.40, -0.65, 1.8),
        (-0.35, -0.55, 2.1), (0.80, -0.30, 2.15), (-0.10, 0.80, 2.0)
    ]
    for ifl, (dx, dy, fz) in enumerate(flower_locs):
        add_cylinder(f"{name}_chuoi_hoa_{ifl}", (lx + dx, ly + dy, lz + fz - 0.25), 0.025, 0.50, mat_flower)

def add_iron_fence(name, x_start, x_end, y_pos, height=2.40, mat_base=None, mat_iron=None):
    """Hàng rào song sắt nghệ thuật trên bệ đá thấp cao 0.4m"""
    width = x_end - x_start
    add_box(f"{name}_BeDa", (x_start, y_pos - 0.12, 0.0), (width, 0.24, 0.40), mat_base)
    iron_h = height - 0.40
    add_box(f"{name}_ThanhDay", (x_start, y_pos - 0.03, 0.40), (width, 0.06, 0.05), mat_iron)
    add_box(f"{name}_ThanhDinh", (x_start, y_pos - 0.03, height - 0.05), (width, 0.06, 0.05), mat_iron)
    num_bars = int(width / 0.16)
    step = width / (num_bars + 1)
    for ib in range(1, num_bars + 1):
        bx = x_start + ib * step
        add_cylinder(f"{name}_Bar_{ib}", (bx, y_pos, 0.43), 0.014, iron_h - 0.08, mat_iron)

def add_sliding_iron_gate(name, x_start, x_end, y_pos, height=2.25, mat_frame=None, mat_rail=None, mat_pillar=None, mat_gold=None):
    """Cổng sắt tự động trượt chạy qua chạy lại 4.0m trên ray"""
    width = x_end - x_start
    # Trụ cổng trái
    add_box(f"{name}_Tru_Trai", (x_start - 0.45, y_pos - 0.35, 0.0), (0.45, 0.45, height + 0.35), mat_pillar)
    add_box(f"{name}_DenTru_Trai", (x_start - 0.38, y_pos - 0.28, height + 0.35), (0.30, 0.30, 0.22), mat_gold)
    # Trụ cổng phải
    add_box(f"{name}_Tru_Phai", (x_end, y_pos - 0.35, 0.0), (0.45, 0.45, height + 0.35), mat_pillar)
    add_box(f"{name}_DenTru_Phai", (x_end + 0.08, y_pos - 0.28, height + 0.35), (0.30, 0.30, 0.22), mat_gold)
    # Thanh ray trượt âm sàn
    add_box(f"{name}_ThanhRay", (x_start - 0.4, y_pos - 0.03, 0.0), (width + 0.8, 0.06, 0.025), mat_rail)
    # Hộp mô tơ tự động
    add_box(f"{name}_MoTo_TuDong", (x_start - 0.40, y_pos + 0.08, 0.02), (0.35, 0.25, 0.42), mat_frame)
    add_cylinder(f"{name}_DenTinHieu", (x_start - 0.22, y_pos + 0.20, 0.45), 0.03, 0.08, mat_gold)
    # Cánh cổng sắt trượt tự động (rộng 4m)
    gate_thick = 0.06
    add_box(f"{name}_KhungDuoi", (x_start, y_pos - gate_thick/2, 0.04), (width, gate_thick, 0.08), mat_frame)
    add_box(f"{name}_KhungTren", (x_start, y_pos - gate_thick/2, height - 0.06), (width, gate_thick, 0.08), mat_frame)
    add_box(f"{name}_KhungTrai", (x_start, y_pos - gate_thick/2, 0.04), (0.08, gate_thick, height - 0.04), mat_frame)
    add_box(f"{name}_KhungPhai", (x_end - 0.08, y_pos - gate_thick/2, 0.04), (0.08, gate_thick, height - 0.04), mat_frame)
    add_box(f"{name}_ThanhNgangGiua", (x_start, y_pos - gate_thick/2, height * 0.45), (width, gate_thick, 0.06), mat_frame)
    num_pickets = 22
    step = (width - 0.16) / (num_pickets + 1)
    for ip in range(1, num_pickets + 1):
        px = x_start + 0.08 + ip * step
        add_cylinder(f"{name}_SongSat_{ip}", (px, y_pos, 0.08), 0.016, height - 0.16, mat_frame)

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
    mat_brick_rustic = create_pbr_material("Brick_GachMocXua",    (0.58, 0.28, 0.16, 1.0), roughness=0.85)
    mat_iron_pot     = create_pbr_material("Metal_GangDenNoi",    (0.12, 0.12, 0.12, 1.0), roughness=0.55, metallic=0.75)
    mat_fire_glow    = create_pbr_material("Light_LuaBepCui",     (1.0, 0.45, 0.10, 1.0), roughness=0.20, emission_color=(1.0, 0.35, 0.05, 1.0), emission_strength=5.0)
    mat_frame_dark   = create_pbr_material("Metal_KhungDoKinh",   (0.12, 0.12, 0.14, 1.0), roughness=0.35, metallic=0.85)

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
    # 4. TƯỜNG RÀO MẶT TIỀN SONG SẮT & CỔNG SẮT TỰ ĐỘNG 4.0M
    # THIẾT KẾ CẢI TẠO THEO YÊU CẦU:
    # 1. Bỏ cổng to Tam Quan, đổi thành CỔNG SẮT TỰ ĐỘNG CHẠY QUA CHẠY LẠI
    # 2. Đường vẫn 8.0m nhưng CỔNG CHỈ 4.0m (X = 7.0 -> 11.0m)
    # 3. TƯỜNG SONG SẮT KÉO RA 2M MỖI BÊN CỔNG (X = 5.0 -> 7.0m & X = 11.0 -> 13.0m)
    # 4. Tường mặt trước làm bằng song sắt xen kẽ với cây xanh
    # 5. Sau phần song sắt 2m: BÊN PHẢI trồng CÂY BƯỞI trĩu quả, BÊN TRÁI trồng CÂY LỘC VỪNG hoa đỏ
    # =========================================================================
    hw = 2.4  # chiều cao tường bao
    tw = 0.22 # độ dày tường
    add_box("TuongRao_Trai", (-tw, 0.0, 0.0), (tw, 37.0, hw), mat_wall)
    add_box("TuongRao_Phai", (18.0, 0.0, 0.0), (tw, 37.0, hw), mat_wall)
    add_box("TuongRao_Sau",  (-tw, 37.0, 0.0), (18.0 + 2*tw, tw, hw), mat_wall)
    add_box("MuNgoi_Trai", (-tw - 0.06, -tw, hw), (tw + 0.12, 37.0 + tw, 0.08), mat_roof_red)
    add_box("MuNgoi_Phai", (18.0 - 0.06, -tw, hw), (tw + 0.12, 37.0 + tw, 0.08), mat_roof_red)
    add_box("MuNgoi_Sau",  (-tw, 37.0 - 0.06, hw), (18.0 + 2*tw, tw + 0.12, 0.08), mat_roof_red)

    # --- HỆ THỐNG MẶT TIỀN: SONG SẮT XEN KẼ CÂY XANH & CỔNG TỰ ĐỘNG 4M ---
    # A. Đoạn mặt tiền bên trái (X = 0.0 -> 5.0m, trước khoảng lùi 2m trồng cau):
    add_iron_fence("SongSat_MatTien_Trai", 0.0, 5.0, 0.0, height=2.40, mat_base=mat_blue_stone, mat_iron=mat_frame_dark)
    # Khóm cây cảnh / bồn hoa xen kẽ hàng rào song sắt
    add_mini_tree("HoaLeo_Fence_Trai1", (1.2, -0.15, 0.0), trunk_r=0.03, height=0.9, foliage_r=0.35, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("HoaLeo_Fence_Trai2", (3.8, -0.15, 0.0), trunk_r=0.03, height=0.9, foliage_r=0.35, wood_mat=mat_wood_dark, leaf_mat=mat_grass)

    # B. Đoạn song sắt kéo ra 2m bên trái cổng (X = 5.0 -> 7.0m):
    add_iron_fence("SongSat_MoRong_Trai_2m", 5.0, 6.6, 0.0, height=2.40, mat_base=mat_blue_stone, mat_iron=mat_frame_dark)

    # C. CỔNG SẮT TỰ ĐỘNG TRƯỢT 4.0M Ở GIỮA TRỤC ĐƯỜNG 8M (X = 7.0 -> 11.0m, Y = 0.0m)
    add_sliding_iron_gate("CongSat_TuDong_4m", 7.0, 11.0, 0.0, height=2.30, mat_frame=mat_frame_dark, mat_rail=mat_chrome, mat_pillar=mat_blue_stone, mat_gold=mat_gold)

    # D. Đoạn song sắt kéo ra 2m bên phải cổng (X = 11.0 -> 13.0m):
    add_iron_fence("SongSat_MoRong_Phai_2m", 11.4, 13.0, 0.0, height=2.40, mat_base=mat_blue_stone, mat_iron=mat_frame_dark)

    # E. Đoạn mặt tiền bên phải (X = 13.0 -> 18.0m, trước khối Bếp & WC):
    add_iron_fence("SongSat_MatTien_Phai", 13.0, 18.0, 0.0, height=2.40, mat_base=mat_blue_stone, mat_iron=mat_frame_dark)
    add_mini_tree("HoaLeo_Fence_Phai1", (14.5, -0.15, 0.0), trunk_r=0.03, height=0.9, foliage_r=0.35, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("HoaLeo_Fence_Phai2", (16.5, -0.15, 0.0), trunk_r=0.03, height=0.9, foliage_r=0.35, wood_mat=mat_wood_dark, leaf_mat=mat_grass)

    # --- CÂY TRỒNG SAU PHẦN SONG SẮT 2M ---
    # 1. Sau song sắt 2m BÊN TRÁI: Trồng CÂY LỘC VỪNG hoa đỏ buông rủ đón tài lộc (X = 5.9, Y = 1.2)
    add_box("BonCay_LocVung", (5.1, 0.1, 0.0), (1.8, 1.8, 0.15), mat_blue_stone)
    add_loc_vung_tree("CayLocVung_CuaNgo", (6.0, 1.0, 0.15), trunk_r=0.16, height=3.5, mat_wood=mat_wood_dark, mat_leaf=mat_grass, mat_flower=mat_carp_red)

    # 2. Sau song sắt 2m BÊN PHẢI: Trồng CÂY BƯỞI trĩu quả vàng óng xum xuê thơm ngát (X = 12.1, Y = 1.2)
    add_box("BonCay_Buoi", (11.1, 0.1, 0.0), (1.8, 1.8, 0.15), mat_blue_stone)
    add_grapefruit_tree("CayBuoi_CuaNgo", (12.0, 1.0, 0.15), trunk_r=0.15, height=3.3, mat_wood=mat_wood_dark, mat_leaf=mat_grass, mat_fruit=mat_lotus_yellow)

    # =========================================================================
    # 5. DÃY BÊN PHẢI (X = 13.0 -> 18.0, Rộng 5.0m, Dài 37.0m)
    # THIẾT KẾ CẢI TẠO NÂNG CẤP THEO YÊU CẦU:
    # 1. Tổng đất cho Bếp & Chỗ Ăn là 14.0m bên phải tính từ cổng vào (Y = 0.0 -> 14.0m)
    # 2. Khối Nhà Vệ Sinh (WC) & Bếp: Tổng ngang 5.0m, dài 2.0m (Y = 0.0 -> 2.0m)
    #    - Nhà vệ sinh chiếm 1.5m chiều rộng (X = 16.5 -> 18.0m, dài 2.0m)
    #      + Xây kín phần thụt vào 1m (X = 17.0 -> 18.0m)
    #      + Cửa nhà vệ sinh hướng về phía nhà ăn (+Y direction)
    #    - Bếp đơn giản không gian mở thôn quê ngày xưa: Chiều rộng 3.5m (X = 13.0 -> 16.5m, dài 2.0m)
    #      + Mở toang về hướng nhà ăn (+Y direction), cột gỗ mộc, bếp kiềng đất nung, chạn tre, bàn đá
    #      + Cả Bếp và WC đều dài 2.0m (rộng bằng nhau theo chiều sâu)
    # 3. Đoạn 2m đệm từ WC/Bếp đến Nhà Ăn (Y = 2.0 -> 4.0m):
    #    - Dọc đoạn tường từ WC đến nhà ăn trồng hàng cây cảnh nhỏ thanh lịch (cau kiểng mini, chuối cảnh)
    #    - Sân đệm lát gạch Bát Tràng và đá bước dạo tự nhiên kết nối sang nhà ăn
    # 4. Nhà Ăn Mái Lá Ở Quê: Dài 7.0m x Rộng 4.0m (X = 13.0 -> 17.0m, Y = 4.0 -> 11.0m)
    #    - Dạng nhà ăn mái lá quê: Các cột gỗ lim tròn tự nhiên xong mái lá, KHÔNG TƯỜNG (mở toang 4 bề đón gió)
    #    - Bàn tiệc gỗ me tây nguyên tấm 4.8m x 1.6m, 10 ghế ăn gỗ lim mộc, đèn nơm tre ấm áp
    # 5. Dải 1m thụt vào (X = 17.0 -> 18.0m, Y = 4.0 -> 11.0m):
    #    - Trưng bày Cối Xay Thóc nan tre -> Rặng trúc cảnh -> Cối Giã Gạo cần đạp chân
    #    - ĐẶC BIỆT: Có MẶT KÍNH nghiêng nối từ đầu tường rào (X=18.0m, Z=2.40m) ra mái nhà ăn (X=17.0m, Z=3.15m)
    #      để ánh nắng tự nhiên rọi thẳng xuống cối xay và cối giã!
    # 6. Đoạn chuyển tiếp còn lại (Y = 11.0 -> 14.0m, Dài 3.0m x Rộng 5.0m):
    #    - Sân thoáng, điểm xuyết hàng cây nhỏ, chậu hoa cảnh trước khi bước vào Chòi Vuông 4x4
    # =========================================================================
    add_box("DaiLui_Phai_1m", (17.0, 0.0, 0.005), (1.0, 37.0, 0.02), mat_paver_gray)

    # --- KHU 3A: KHỐI NHÀ VỆ SINH & BẾP MỞ QUÊ (Y = 0.0 -> 2.0m, Rộng 5.0m, Dài 2.0m) ---
    # 1. NHÀ VỆ SINH (WC) (X = 16.5 -> 18.0m, Rộng 1.5m, Dài 2.0m)
    # Xây kín phần thụt vào 1m (X = 17.0 -> 18.0m) và thêm 0.5m (X = 16.5 -> 17.0m)
    add_box("WC_TuongTay", (16.5, 0.0, 0.0), (0.12, 2.0, 2.8), mat_wall)
    # Tường Bắc có ô cửa hướng thẳng về nhà ăn
    add_box("WC_TuongBac_Trai", (16.5, 1.88, 0.0), (0.22, 0.12, 2.8), mat_wall)
    add_box("WC_TuongBac_Phai", (17.47, 1.88, 0.0), (0.53, 0.12, 2.8), mat_wall)
    add_box("WC_LanhTo_Cua",   (16.72, 1.88, 2.10), (0.75, 0.12, 0.70), mat_wall)
    # Cửa nhà vệ sinh mở về hướng nhà ăn (+Y)
    add_box("WC_Cua_Go", (16.74, 1.90, 0.02), (0.71, 0.04, 2.06), mat_wood_door)
    add_cylinder("WC_TayNam", (17.38, 1.93, 1.0), 0.015, 0.10, mat_brass)
    # Sàn đá slate WC chống trơn
    add_box("WC_San_Slate", (16.62, 0.05, 0.02), (1.36, 1.85, 0.04), mat_slate_wc)
    # Thiết bị WC: Bồn cầu sứ, bệ lavabo đá đen & chậu sứ, vòi sen, gương soi
    add_box("WC_BonCau_De", (17.20, 0.35, 0.05), (0.42, 0.55, 0.42), mat_ceramic_wc)
    add_cylinder("WC_BonCau_KetNuoc", (17.41, 0.22, 0.45), 0.18, 0.45, mat_ceramic_wc)
    add_box("WC_BanLavabo", (17.15, 1.25, 0.05), (0.50, 0.52, 0.82), mat_black_marble)
    add_cylinder("WC_ChauRua", (17.40, 1.50, 0.85), 0.15, 0.10, mat_ceramic_wc)
    add_box("WC_GuongSoi", (17.95, 1.30, 1.15), (0.02, 0.42, 0.65), mat_glass)
    add_cylinder("WC_VoiSen", (17.10, 0.80, 1.20), 0.015, 0.80, mat_chrome)
    add_box("WC_Tran", (16.50, 0.0, 2.80), (1.50, 2.0, 0.10), mat_wall)
    add_light_source("Light_WC", (17.25, 1.0, 2.65), energy=25.0, color=(1.0, 0.95, 0.90))

    # 2. BẾP ĐƠN GIẢN KHÔNG GIAN MỞ NGÀY XƯA (X = 13.0 -> 16.5m, Rộng 3.5m, Dài 2.0m)
    # Tường hậu gạch mộc phía Nam (Y = 0)
    add_box("Bep_TuongHau", (13.0, 0.0, 0.0), (3.5, 0.18, 3.0), mat_brick_rustic)
    # Phía Tây giáp đường 8m: Cột gỗ đỡ mái & tường quầy bếp lửng
    add_cylinder("Cot_Bep_Tay1", (13.15, 0.15, 0.0), 0.11, 2.95, mat_wood_dark)
    add_cylinder("Cot_Bep_Tay2", (13.15, 1.85, 0.0), 0.11, 2.95, mat_wood_dark)
    add_box("Bep_TuongLung_Tay", (13.05, 0.25, 0.0), (0.20, 1.50, 0.80), mat_brick_rustic)
    add_box("Bep_MatQuay_Tay",   (13.00, 0.20, 0.80), (0.30, 1.60, 0.05), mat_blue_stone)
    # Phía Bắc (hướng về nhà ăn): Mở toang hoàn toàn, có cột góc và xà gỗ giằng trên cao
    add_cylinder("Cot_Bep_GocBac", (16.40, 1.88, 0.0), 0.10, 2.95, mat_wood_dark)
    add_box("XaNgang_Bep_Bac", (13.05, 1.88, 2.95), (3.45, 0.12, 0.14), mat_wood_dark)
    # Sàn Bếp gạch Bát Tràng cổ truyền
    add_box("Bep_San_GachBatTrang", (13.0, 0.0, 0.01), (3.5, 2.0, 0.05), mat_terracotta_floor)
    # Bếp lò củi đôi bằng đất sét nung, 2 miệng kiềng gang, lửa than hồng bập bùng
    add_box("BepLo_ThanDat", (14.60, 0.25, 0.06), (1.40, 0.80, 0.55), mat_brick_rustic)
    add_cylinder("BepLo_Mieng1", (14.95, 0.65, 0.58), 0.18, 0.06, mat_iron_pot)
    add_cylinder("BepLo_Mieng2", (15.65, 0.65, 0.58), 0.18, 0.06, mat_iron_pot)
    add_cylinder("BepLo_LuaThan1", (14.95, 0.65, 0.35), 0.12, 0.05, mat_fire_glow)
    add_cylinder("BepLo_LuaThan2", (15.65, 0.65, 0.35), 0.12, 0.05, mat_fire_glow)
    add_light_source("Light_LuaBep", (15.30, 0.65, 0.65), energy=35.0, color=(1.0, 0.45, 0.10))
    # 2 Nồi gang đen truyền thống & ấm đun nước đồng cổ
    add_cylinder("NoiGang_1", (14.95, 0.65, 0.64), 0.16, 0.18, mat_iron_pot)
    add_cylinder("NoiGang_2", (15.65, 0.65, 0.64), 0.14, 0.15, mat_iron_pot)
    add_cone("VungNoi_1", (14.95, 0.65, 0.82), 0.17, 0.06, mat_iron_pot)
    add_cylinder("AmNuocDong", (15.28, 0.38, 0.61), 0.09, 0.15, mat_wash_tub)
    add_cylinder("OngKhoi_Bep", (15.30, 0.25, 0.55), 0.08, 3.40, mat_brick_rustic)
    # Bàn sơ chế thức ăn mặt đá xanh mộc mạc
    add_box("BanSoChe_Than", (13.35, 0.25, 0.06), (1.10, 0.75, 0.75), mat_wood_warm)
    add_box("BanSoChe_MatDa", (13.30, 0.20, 0.81), (1.20, 0.85, 0.05), mat_blue_stone)
    add_cylinder("ChauRua_Gom", (13.60, 0.60, 0.86), 0.16, 0.12, mat_clay_mill)
    # Kệ chạn bát nan tre mộc mạc & bát đĩa gốm
    add_box("ChanBat_Tre", (13.50, 0.12, 1.45), (1.20, 0.26, 0.70), mat_bamboo)
    add_cylinder("BatGom_1", (13.80, 0.20, 1.55), 0.07, 0.05, mat_clay_mill)
    add_cylinder("BatGom_2", (14.10, 0.20, 1.55), 0.07, 0.05, mat_clay_mill)
    # Bó củi khô xếp gọn gầm kệ bếp, nia tre treo tường
    add_box("GiaDoCui", (13.35, 1.15, 0.06), (0.80, 0.60, 0.10), mat_wood_dark)
    add_cylinder("BoCui_1", (13.55, 1.45, 0.16), 0.12, 0.65, mat_wood_dark)
    add_cylinder("BoCui_2", (13.80, 1.45, 0.16), 0.10, 0.65, mat_wood_dark)
    add_cylinder("NiaTre_Treo", (14.10, 0.17, 2.30), 0.25, 0.02, mat_bamboo, vertices=16)
    # Đèn nơm tre ấm cúng
    add_cone("DenNomTre_Bep", (14.80, 1.20, 2.60), 0.22, 0.35, mat_bamboo)
    add_light_source("Light_TranBep", (14.80, 1.20, 2.45), energy=30.0, color=(1.0, 0.90, 0.75))
    # Mái ngói đỏ che khối Bếp & WC
    add_gabled_roof("Mai_KhoiBep_WC", 12.8, 18.2, -0.2, 2.2, 3.0, 3.95, overhang=0.35, material=mat_roof_red)

    # --- KHU 3B: ĐOẠN ĐỆM 2M CÓ HÀNG CÂY XANH (Y = 2.0 -> 4.0m, Dài 2.0m x Rộng 5.0m) ---
    # Sân đệm lát gạch Bát Tràng và đá xanh bazan kết nối thông thoáng
    add_box("SanDem_2m_Nen", (13.0, 2.0, 0.005), (3.5, 2.0, 0.025), mat_terracotta_floor)
    add_cylinder("DaBuoc_SanDem_1", (14.8, 2.6, 0.03), 0.26, 0.03, mat_blue_stone)
    add_cylinder("DaBuoc_SanDem_2", (15.5, 3.3, 0.03), 0.26, 0.03, mat_blue_stone)
    add_cylinder("DaBuoc_SanDem_3", (16.8, 2.6, 0.03), 0.24, 0.03, mat_blue_stone)
    # Bồn cỏ xanh & hàng cây cảnh nhỏ dọc tường từ WC đến nhà ăn (X = 16.5 -> 18.0, Y = 2.0 -> 4.0m)
    add_box("BonCay_2m_Co", (16.5, 2.0, 0.01), (1.5, 2.0, 0.04), mat_grass)
    add_box("BoDa_BonCay_2m", (16.42, 2.0, 0.0), (0.08, 2.0, 0.12), mat_blue_stone)
    add_mini_tree("CauKieng_2m_1", (17.2, 2.5, 0.05), trunk_r=0.05, height=1.6, foliage_r=0.45, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("CauKieng_2m_2", (17.3, 3.1, 0.05), trunk_r=0.05, height=1.8, foliage_r=0.50, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("CauKieng_2m_3", (17.1, 3.7, 0.05), trunk_r=0.04, height=1.5, foliage_r=0.40, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    # 2 Bụi hoa nhỏ mép đường 8m
    add_mini_tree("BuiHoa_MepDuong_1", (13.25, 2.6, 0.0), trunk_r=0.03, height=0.7, foliage_r=0.30, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("BuiHoa_MepDuong_2", (13.25, 3.5, 0.0), trunk_r=0.03, height=0.7, foliage_r=0.30, wood_mat=mat_wood_dark, leaf_mat=mat_grass)

    # --- KHU 3C: NHÀ ĂN MÁI LÁ Ở QUÊ (Y = 4.0 -> 11.0m, Dài 7.0m x Rộng 4.0m) ---
    # Nền gạch Bát Tràng truyền thống có gờ đá xanh
    add_box("NhaAn_Nen_Gach", (13.0, 4.0, 0.02), (4.0, 7.0, 0.08), mat_terracotta_floor)
    add_box("NhaAn_GoDa_Vien", (12.95, 3.95, 0.0), (4.10, 7.10, 0.03), mat_blue_stone)
    # Hệ cột gỗ tròn tự nhiên vững chãi (KHÔNG TƯỜNG - MỞ TOANG 4 BỀ ĐÓN GIÓ)
    cot_y_list = [4.3, 6.5, 8.7, 10.7]
    for yp in cot_y_list:
        add_cylinder(f"ChanTang_CotAn_Trai_{yp}", (13.20, yp, 0.10), 0.16, 0.12, mat_blue_stone)
        add_cylinder(f"Cot_NhaAn_Trai_{yp}",      (13.20, yp, 0.22), 0.11, 2.95, mat_wood_dark)
        add_cylinder(f"ChanTang_CotAn_Phai_{yp}", (16.80, yp, 0.10), 0.16, 0.12, mat_blue_stone)
        add_cylinder(f"Cot_NhaAn_Phai_{yp}",      (16.80, yp, 0.22), 0.11, 2.95, mat_wood_dark)
        add_box(f"XaNgang_NhaAn_{yp}", (13.20, yp - 0.06, 3.08), (3.60, 0.12, 0.14), mat_wood_dark)
    # Xà dọc giằng mái 2 bên
    add_box("XaDoc_NhaAn_Trai", (13.14, 4.1, 3.10), (0.12, 6.8, 0.14), mat_wood_dark)
    add_box("XaDoc_NhaAn_Phai", (16.74, 4.1, 3.10), (0.12, 6.8, 0.14), mat_wood_dark)
    # Mái lá ở quê (Mái dốc 2 mái rơm rạ / lá cọ dày dặn)
    add_gabled_roof("Mai_NhaAn_MaiLa", 12.6, 17.4, 3.65, 11.35, 3.15, 4.35, overhang=0.45, material=mat_thatch_leaf)
    add_box("BoNoc_MaiLa", (14.90, 3.55, 4.35), (0.20, 8.0, 0.16), mat_thatch_ridge)
    for ybn in range(4, 12, 2):
        add_cylinder(f"BoNoc_DayCot_{ybn}", (15.0, ybn, 4.35), 0.12, 0.18, mat_bamboo)
    # Đèn nơm tre dân dã treo thả trần ấm áp
    for y_light, l_idx in [(5.5, 1), (7.5, 2), (9.5, 3)]:
        add_cylinder(f"DayTreo_Den_{l_idx}", (15.0, y_light, 3.5), 0.015, 0.6, mat_wood_dark)
        add_cone(f"DenNomTre_{l_idx}", (15.0, y_light, 2.9), 0.28, 0.45, mat_bamboo)
        add_light_source(f"Den_NhaAn_{l_idx}", (15.0, y_light, 2.7), energy=45.0, color=(1.0, 0.88, 0.70))
    # Bàn ăn tiệc gỗ me tây nguyên tấm dân dã thôn quê
    add_box("BanAn_ThonQue_Than", (14.25, 5.2, 0.0), (1.50, 4.6, 0.72), mat_wood_warm)
    add_box("BanAn_ThonQue_Mat",  (14.10, 5.0, 0.72), (1.80, 5.0, 0.08), mat_wood_dark)
    for ig in range(4):
        add_chair(f"GheAn_Trai_{ig}", (13.55, 5.4 + ig*1.15, 0.0), mat_wood_dark)
        add_chair(f"GheAn_Phai_{ig}", (16.25, 5.4 + ig*1.15, 0.0), mat_wood_dark)
    add_chair("GheAn_Dau1", (15.0, 4.6, 0.0), mat_wood_dark)
    add_chair("GheAn_Dau2", (15.0, 10.4, 0.0), mat_wood_dark)

    # --- KHU 3D: DẢI 1M THỤT VÀO VỚI MẶT KÍNH LẤY SÁNG RỌI CỐI XAY & CỐI GIÃ (X = 17.0 -> 18.0m, Y = 4.0 -> 11.0m) ---
    add_box("NenSoi_KyVat", (17.02, 4.0, 0.02), (0.96, 7.0, 0.04), mat_pebble)
    for yst in [4.8, 6.0, 7.4, 8.8, 10.2]:
        add_cylinder(f"DaBuoc_KyVat_{yst}", (17.5, yst, 0.04), 0.22, 0.03, mat_blue_stone)
    # Cối xay thóc nan tre truyền thống (tại Y = 6.0m)
    add_cylinder("CoiXay_ThotDuoi", (17.5, 6.0, 0.06), 0.38, 0.42, mat_clay_mill)
    add_cylinder("CoiXay_VanhTre",  (17.5, 6.0, 0.06), 0.40, 0.40, mat_wood_warm)
    add_cylinder("CoiXay_ThotTren", (17.5, 6.0, 0.48), 0.35, 0.35, mat_clay_mill)
    add_box("CoiXay_CanGiang", (17.18, 5.96, 1.05), (0.64, 0.08, 0.08), mat_wood_dark)
    add_light_source("Spot_CoiXay", (17.5, 6.0, 2.6), energy=50.0, color=(1.0, 0.90, 0.75))
    # Rặng trúc quân tử xanh mát ngăn giữa 2 cụm kỷ vật
    for ytr in [7.4, 7.7, 8.0]:
        add_cylinder(f"TrucCanh_{ytr}", (17.75, ytr, 0.0), 0.03, 2.4, mat_grass)
        add_cone(f"LaTruc_{ytr}", (17.75, ytr, 1.8), 0.32, 0.8, mat_grass)
    # Cối giã gạo cần đạp chân cổ truyền (tại Y = 9.4m)
    add_cylinder("CoiGia_CoiDa", (17.5, 9.4, 0.06), 0.34, 0.44, mat_blue_stone)
    add_box("CoiGia_CanDap", (17.44, 9.3, 0.40), (0.12, 2.0, 0.12), mat_wood_dark)
    add_cylinder("CoiGia_Chay", (17.5, 9.4, 0.15), 0.07, 0.35, mat_wood_dark)
    add_light_source("Spot_CoiGia", (17.5, 9.4, 2.6), energy=50.0, color=(1.0, 0.90, 0.75))
    # MẶT KÍNH NỐI TỪ ĐẦU TƯỜNG (X = 18.0m, Z = 2.40m) RA MÁI NHÀ ĂN (X = 17.0m, Z = 3.15m) ĐỂ ÁNH NẮNG RỌI XUỐNG
    add_slanted_glass_roof("MaiKinh_KyVat_Skylight", 17.0, 3.15, 18.0, 2.40, 4.0, 11.0, thickness=0.015, material=mat_glass)
    # Hệ đòn tay kim loại đỡ kính cường lực
    dx_k, dz_k = 1.0, -0.75
    dist_k = math.sqrt(dx_k*dx_k + dz_k*dz_k)
    ang_pitch_k = math.atan2(dz_k, dx_k)
    for y_frame in [4.0, 5.4, 6.8, 8.2, 9.6, 11.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(17.5, y_frame, 2.76), scale=(dist_k, 0.04, 0.05))
        fra = bpy.context.active_object
        fra.name = f"KhungKinh_Ngang_{y_frame}"
        fra.rotation_euler = (0, -ang_pitch_k, 0)
        fra.data.materials.append(mat_frame_dark)
    add_box("KhungKinh_Doc_Tren", (16.96, 4.0, 3.10), (0.06, 7.0, 0.06), mat_frame_dark)
    add_box("KhungKinh_Doc_Duoi", (17.96, 4.0, 2.37), (0.06, 7.0, 0.06), mat_frame_dark)

    # --- KHU 3E: ĐOẠN CHUYỂN TIẾP CÒN LẠI (Y = 11.0 -> 14.0m, Dài 3.0m x Rộng 5.0m) ---
    add_box("San_ChuyenTiep_11_14", (13.0, 11.0, 0.005), (5.0, 3.0, 0.025), mat_paver_gray)
    add_cylinder("DaBuoc_ChuyenTiep_1", (15.0, 11.8, 0.03), 0.35, 0.03, mat_blue_stone)
    add_cylinder("DaBuoc_ChuyenTiep_2", (15.0, 13.0, 0.03), 0.35, 0.03, mat_blue_stone)
    add_mini_tree("CayCanh_Nho_1", (17.4, 11.8, 0.03), trunk_r=0.04, height=1.4, foliage_r=0.45, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("CayCanh_Nho_2", (17.4, 13.2, 0.03), trunk_r=0.04, height=1.5, foliage_r=0.48, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("BuiHoa_Nho_1", (13.3, 12.2, 0.03), trunk_r=0.03, height=0.7, foliage_r=0.32, wood_mat=mat_wood_dark, leaf_mat=mat_grass)
    add_mini_tree("BuiHoa_Nho_2", (13.3, 13.4, 0.03), trunk_r=0.03, height=0.7, foliage_r=0.32, wood_mat=mat_wood_dark, leaf_mat=mat_grass)

    # --- KHU 2: NHÀ / CHÒI VUÔNG 4.0m x 4.0m & 2 SÂN THOÁNG (Y = 13.5 -> 25.5m, 12.0m) ---
    # Sân nền tổng Khu 2
    add_box("San_Khu2_Tong", (13.0, 14.0, 0.005), (4.0, 11.5, 0.025), mat_paver_gray)
    
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
    # THIẾT KẾ CẢI TẠO THEO CHỈ ĐẠO CỦA GIA CHỦ:
    # 1. Dãy Trái thụt vào 2m: Hàng Cau Ta truyền thống (Y = 0.0 -> 2.0m)
    # 2. Căn 1 (6x4, Y = 2.0 -> 8.0m): Cửa vào bên trái (gần cổng), WC ở phía Bắc
    # 3. Căn 2 (6x4, Y = 8.0 -> 14.0m): Cửa vào bên phải (gần ao), WC ở phía Nam
    #    ==> 2 NHÀ VỆ SINH CỦA 2 PHÒNG DỰA LƯNG VÀO NHAU TẠI VÁCH CHUNG Y = 8.0M!
    # 4. Khoảng cách 1m: Lối đi giữa Cụm 2 phòng và Ao cá (Y = 14.0 -> 15.0m)
    # 5. Cái Ao Cá Quê 6x5 (Y = 15.0 -> 21.0m, X = 0.0 -> 5.0m, lấy luôn lối đi 1m):
    #    Bờ nhỏ kè đá, bậc thang đá đi xuống (mặt nước ngập giữa bậc 2), cá chép, hoa sen, bến giặt xưa
    # 6. Khoảng cách 1m: Lối đi giữa Ao cá và Căn 3 (Y = 21.0 -> 22.0m)
    # 7. Căn 3 (6x4, Y = 22.0 -> 28.0m): Nhà nghỉ view ao và vườn hoa
    # 8. Cái Vườn Rút Gọn 9m (Y = 28.0 -> 37.0m):
    #    Hàng rào hoa 70cm mặt trước, lối vào ở giữa, hoa 2 bên lối vào;
    #    Nhìn vào: Bên phải trồng rau sạch, bên trái trồng cây ăn trái,
    #    Cuối góc phải gần tường là Chuồng Gà quê truyền thống!
    # =========================================================================

    # Thêm vật liệu cho Vườn Rau, Hoa và Chuồng Gà
    mat_soil         = create_pbr_material("Nature_DatTrongRau",  (0.24, 0.16, 0.10, 1.0), roughness=0.95)
    mat_veggie       = create_pbr_material("Nature_RauXanhNon",   (0.20, 0.62, 0.12, 1.0), roughness=0.55)
    mat_flower_red   = create_pbr_material("Flower_HoaDoTham",    (0.88, 0.10, 0.14, 1.0), roughness=0.45)
    mat_flower_ylw   = create_pbr_material("Flower_HoaVangRuc",   (0.96, 0.82, 0.08, 1.0), roughness=0.45)
    mat_flower_pur   = create_pbr_material("Flower_HoaTimBiec",   (0.68, 0.22, 0.75, 1.0), roughness=0.45)
    mat_chicken_coop = create_pbr_material("Wood_ChuongGaQue",   (0.30, 0.18, 0.10, 1.0), roughness=0.75)
    mat_straw        = create_pbr_material("Deco_RomRaONam",      (0.78, 0.62, 0.28, 1.0), roughness=0.90)
    mat_chicken_comb = create_pbr_material("Animal_MaoGaDoTuoi",  (0.92, 0.06, 0.04, 1.0), roughness=0.35)
    mat_chicken_body = create_pbr_material("Animal_LongGaTia",    (0.65, 0.22, 0.08, 1.0), roughness=0.60)
    mat_chicken_gold = create_pbr_material("Animal_LongGaMaiVang",(0.82, 0.60, 0.15, 1.0), roughness=0.65)
    mat_wire_mesh    = create_pbr_material("Metal_LuoiMatCao",    (0.40, 0.42, 0.44, 1.0), roughness=0.40, metallic=0.75)

    # Dải lùi ngoài tường rào (chỉ ở khu vực nhà)
    add_box("DaiLui_Trai_Nha1_2", (0.0, 2.0, 0.005), (1.0, 12.0, 0.02), mat_paver_gray)
    add_box("DaiLui_Trai_Nha3",   (0.0, 22.0, 0.005), (1.0, 6.0, 0.02), mat_paver_gray)

    # --- KHU 6A: KHOẢNG LÙI 2M TRỒNG HÀNG CÂY CAU TRUYỀN THỐNG (Y = 0.0 -> 2.0m) ---
    add_box("SanCo_HangCau", (0.0, 0.0, 0.01), (5.0, 2.0, 0.04), mat_grass)
    add_box("BoDa_HangCau", (4.88, 0.0, 0.0), (0.12, 2.0, 0.08), mat_blue_stone)
    add_areca_palm("CauTa_1", (1.0, 1.0, 0.04), height=4.2, mat_trunk=mat_wood_dark, mat_frond=mat_grass, mat_fruit=mat_lotus_yellow)
    add_areca_palm("CauTa_2", (2.0, 1.0, 0.04), height=4.0, mat_trunk=mat_wood_dark, mat_frond=mat_grass, mat_fruit=mat_lotus_yellow)
    add_areca_palm("CauTa_3", (3.0, 1.0, 0.04), height=4.4, mat_trunk=mat_wood_dark, mat_frond=mat_grass, mat_fruit=mat_lotus_yellow)
    add_areca_palm("CauTa_4", (4.0, 1.0, 0.04), height=3.8, mat_trunk=mat_wood_dark, mat_frond=mat_grass, mat_fruit=mat_lotus_yellow)
    add_cylinder("DaBuoc_HangCau_1", (2.5, 0.5, 0.04), 0.25, 0.03, mat_blue_stone)
    add_cylinder("DaBuoc_HangCau_2", (2.5, 1.5, 0.04), 0.25, 0.03, mat_blue_stone)

    # --- HÀM TẠO CĂN NHÀ NGHỈ DƯỠNG CẢI TẠO BỐ CỤC THEO YÊU CẦU ---
    # door_pos: "left" (cửa bên trái) hoặc "right" (cửa bên phải)
    # wc_pos: "north" (WC ở đầu Bắc) hoặc "south" (WC ở đầu Nam)
    def build_custom_house_6x4(prefix, y_start, door_pos="left", wc_pos="south", room_type="master"):
        # Sàn nhà & khung tường bao
        add_box(f"{prefix}_San", (1.0, y_start, 0.01), (4.0, 6.0, 0.06), mat_wood_floor)
        add_box(f"{prefix}_TuongTrai", (1.0, y_start, 0.0), (0.18, 6.0, 3.2), mat_wall)
        add_box(f"{prefix}_TuongDau",  (1.0, y_start, 0.0), (4.0, 0.18, 3.2), mat_wall)
        add_box(f"{prefix}_TuongCuoi", (1.0, y_start + 5.82, 0.0), (4.0, 0.18, 3.2), mat_wall)
        add_box(f"{prefix}_TuongPhai_Thap",    (4.82, y_start, 0.0), (0.18, 6.0, 0.8), mat_wall)
        add_box(f"Mai_{prefix}_TuongPhai_Cao", (4.82, y_start, 0.8), (0.18, 6.0, 2.4), mat_wall)

        # Cửa ra vào mặt tiền (giáp đại lộ X = 4.82m):
        # "left": cửa ở phía bên trái (gần cổng hơn / Y nhỏ hơn)
        # "right": cửa ở phía bên phải (gần ao hơn / Y lớn hơn)
        if door_pos == "left":
            door_y = y_start + 0.65
            win_y  = y_start + 3.0
            add_box(f"{prefix}_KhungCua", (4.78, door_y, 0.0), (0.06, 1.20, 2.20), mat_wood_dark)
            add_box(f"{prefix}_Cua",      (4.80, door_y + 0.05, 0.02), (0.04, 1.10, 2.15), mat_wood_dark)
            add_box(f"{prefix}_CuaSoKinh", (4.80, win_y, 1.0), (0.04, 2.2, 1.5), mat_glass)
        else: # "right"
            door_y = y_start + 4.15
            win_y  = y_start + 1.2
            add_box(f"{prefix}_KhungCua", (4.78, door_y, 0.0), (0.06, 1.20, 2.20), mat_wood_dark)
            add_box(f"{prefix}_Cua",      (4.80, door_y + 0.05, 0.02), (0.04, 1.10, 2.15), mat_wood_dark)
            add_box(f"{prefix}_CuaSoKinh", (4.80, win_y, 1.0), (0.04, 2.2, 1.5), mat_glass)

        # Cửa sổ kính view ao cá ở tường đầu/cuối nếu có
        if room_type == "view_ao":
            add_box(f"{prefix}_CuaSo_ViewAo", (2.0, y_start + 5.80, 0.9), (2.0, 0.06, 1.6), mat_glass)

        # Nhà vệ sinh (WC): Rộng 1.6m (X: 1.18 -> 2.78m), Sâu 1.7m
        # Nếu wc_pos == "north": WC đặt ở đầu Bắc (giáp vách y_start + 6.0m)
        # Nếu wc_pos == "south": WC đặt ở đầu Nam (giáp vách y_start)
        if wc_pos == "north":
            wc_y_min = y_start + 4.12
            wc_y_max = y_start + 5.82
            # Vách ngăn WC
            add_box(f"{prefix}_WC_TuongDoc",   (2.68, wc_y_min, 0.0), (0.10, 1.70, 2.6), mat_wall)
            add_box(f"{prefix}_WC_TuongNgang", (1.18, wc_y_min, 0.0), (1.60, 0.10, 2.6), mat_wall)
            add_box(f"{prefix}_WC_Cua",        (1.88, wc_y_min - 0.02, 0.0), (0.75, 0.04, 2.1), mat_wood_dark)
            add_box(f"{prefix}_WC_San",        (1.18, wc_y_min, 0.02), (1.50, 1.70, 0.04), mat_slate_wc)
            add_box(f"{prefix}_WC_Lavabo",     (2.10, wc_y_min + 0.20, 0.05), (0.50, 0.45, 0.82), mat_black_marble)
            add_cylinder(f"{prefix}_WC_Chau",  (2.35, wc_y_min + 0.42, 0.85), 0.15, 0.10, mat_ceramic_wc)
            add_box(f"{prefix}_WC_Toilet",     (2.10, wc_y_min + 1.05, 0.05), (0.45, 0.55, 0.45), mat_ceramic_wc)
        else: # "south"
            wc_y_min = y_start + 0.18
            wc_y_max = y_start + 1.88
            add_box(f"{prefix}_WC_TuongDoc",   (2.68, wc_y_min, 0.0), (0.10, 1.70, 2.6), mat_wall)
            add_box(f"{prefix}_WC_TuongNgang", (1.18, wc_y_max, 0.0), (1.60, 0.10, 2.6), mat_wall)
            add_box(f"{prefix}_WC_Cua",        (1.88, wc_y_max - 0.02, 0.0), (0.75, 0.04, 2.1), mat_wood_dark)
            add_box(f"{prefix}_WC_San",        (1.18, wc_y_min, 0.02), (1.50, 1.70, 0.04), mat_slate_wc)
            add_box(f"{prefix}_WC_Lavabo",     (2.10, wc_y_min + 0.30, 0.05), (0.50, 0.45, 0.82), mat_black_marble)
            add_cylinder(f"{prefix}_WC_Chau",  (2.35, wc_y_min + 0.52, 0.85), 0.15, 0.10, mat_ceramic_wc)
            add_box(f"{prefix}_WC_Toilet",     (2.10, wc_y_min + 1.15, 0.05), (0.45, 0.55, 0.45), mat_ceramic_wc)

        # Nội thất phòng ngủ
        if wc_pos == "north":
            # Giường ngủ đặt ở phần phía Nam (Y nhỏ hơn)
            add_box(f"{prefix}_Giuong_Khung", (1.60, y_start + 1.30, 0.05), (1.90, 2.10, 0.40), mat_wood_warm)
            add_box(f"{prefix}_Giuong_Nem",   (1.68, y_start + 1.38, 0.45), (1.74, 1.94, 0.22), mat_white_linen)
            add_box(f"{prefix}_Giuong_Goi1",  (1.85, y_start + 1.45, 0.67), (0.55, 0.38, 0.10), mat_pillow)
            add_box(f"{prefix}_Giuong_Goi2",  (2.65, y_start + 1.45, 0.67), (0.55, 0.38, 0.10), mat_pillow)
            add_box(f"{prefix}_TuAo",         (3.70, y_start + 0.25, 0.05), (0.95, 0.55, 2.30), mat_wood_dark)
        else: # wc_pos == "south"
            # Giường ngủ đặt ở phần phía Bắc (Y lớn hơn)
            add_box(f"{prefix}_Giuong_Khung", (1.60, y_start + 2.80, 0.05), (1.90, 2.10, 0.40), mat_wood_warm)
            add_box(f"{prefix}_Giuong_Nem",   (1.68, y_start + 2.88, 0.45), (1.74, 1.94, 0.22), mat_white_linen)
            add_box(f"{prefix}_Giuong_Goi1",  (1.85, y_start + 4.35, 0.67), (0.55, 0.38, 0.10), mat_pillow)
            add_box(f"{prefix}_Giuong_Goi2",  (2.65, y_start + 4.35, 0.67), (0.55, 0.38, 0.10), mat_pillow)
            add_box(f"{prefix}_TuAo",         (3.70, y_start + 2.30, 0.05), (0.95, 0.55, 2.30), mat_wood_dark)
            if room_type == "view_ao":
                add_box(f"{prefix}_BanTraView", (3.60, y_start + 4.50, 0.05), (0.80, 1.00, 0.45), mat_wood_dark)

        add_light_source(f"Light_{prefix}", (3.0, y_start + 3.0, 2.5), energy=30.0, color=(1.0, 0.92, 0.82))
        add_gabled_roof(f"Mai_{prefix}", 0.8, 5.2, y_start, y_start + 6.0, 3.2, 4.35, overhang=0.35, material=mat_roof_red)

    # 1. CĂN 1 (6x4, Y = 2.0 -> 8.0m): Phòng gần cổng, Cửa vào bên trái, WC phía Bắc (tựa vào vách Y = 8.0m)
    build_custom_house_6x4("NhaKhach1_6x4", 2.0, door_pos="left", wc_pos="north", room_type="master")

    # 2. CĂN 2 (6x4, Y = 8.0 -> 14.0m): Phòng nối tiếp, Cửa vào bên phải, WC phía Nam (tựa vào vách Y = 8.0m)
    # ==> 2 WC DỰA LƯNG NHAU HOÀN TOÀN TẠI VÁCH Y = 8.0M!
    build_custom_house_6x4("NhaKhach2_6x4", 8.0, door_pos="right", wc_pos="south", room_type="view_ao")

    # 3. KHOẢNG CÁCH 1M GIỮA CỤM 2 PHÒNG VÀ AO CÁ (Y = 14.0 -> 15.0m)
    add_box("SanDem_Nha2_AoCa", (0.0, 14.0, 0.01), (5.0, 1.0, 0.04), mat_grass)
    add_cylinder("DaBuoc_Dem1_1", (1.8, 14.5, 0.04), 0.25, 0.03, mat_blue_stone)
    add_cylinder("DaBuoc_Dem1_2", (3.2, 14.5, 0.04), 0.25, 0.03, mat_blue_stone)
    add_cylinder("BuiHoa_Dem1_1", (0.8, 14.5, 0.04), 0.20, 0.35, mat_flower_red)
    add_cylinder("BuiHoa_Dem1_2", (4.4, 14.5, 0.04), 0.20, 0.35, mat_flower_ylw)

    # 4. CÁI AO CÁ QUÊ 6x5 (Y = 15.0 -> 21.0m, X = 0.0 -> 5.0m, LẤY LUÔN LỐI ĐI 1M)
    # Đáy ao sâu -0.70m, cát sỏi tự nhiên
    add_box("DayAo_SanDatCat", (0.15, 15.15, -0.70), (4.70, 5.70, 0.05), mat_pond_bottom)
    # Bờ tường ao xung quanh
    add_box("ThanhAo_Nam",  (0.00, 15.00, -0.70), (5.00, 0.15, 0.75), mat_pond_wall)
    add_box("ThanhAo_Bac",  (0.00, 20.85, -0.70), (5.00, 0.15, 0.75), mat_pond_wall)
    add_box("ThanhAo_Tay",  (0.00, 15.00, -0.70), (0.15, 6.00, 0.75), mat_pond_wall)
    add_box("ThanhAo_Dong", (4.85, 15.00, -0.70), (0.15, 6.00, 0.75), mat_pond_wall)

    # Bờ nhỏ xếp đá cuội tự nhiên bo quanh ao
    for ix in range(9):
        rx = 0.30 + ix * 0.55
        add_sphere(f"DaBoAo_Nam_{ix}", (rx, 15.08, 0.02), radius=0.18, scale=(1.2, 0.9, 0.65), material=mat_rock_river)
        add_sphere(f"DaBoAo_Bac_{ix}", (rx, 20.92, 0.02), radius=0.20, scale=(1.1, 0.8, 0.70), material=mat_rock_river)
    for iy in range(9):
        ry = 15.45 + iy * 0.60
        add_sphere(f"DaBoAo_Tay_{iy}", (0.10, ry, 0.02), radius=0.20, scale=(0.8, 1.2, 0.65), material=mat_rock_river)
        # Chừa khoảng bờ phía đông cho bậc thang đá đi xuống
        if not (17.0 <= ry <= 19.0):
            add_sphere(f"DaBoAo_Dong_{iy}", (4.90, ry, 0.02), radius=0.20, scale=(0.85, 1.1, 0.65), material=mat_rock_river)

    # MẶT NƯỚC AO CÁ: Đặt ở Z = -0.08m
    # Nước ngập đến tầm giữa bậc 2 (bậc 2 đỉnh -0.04m, đáy -0.12m, nước -0.08m chính giữa!)
    add_box("MatNuoc_AoCa_TrongSuot", (0.16, 15.16, -0.08), (4.68, 5.68, 0.04), mat_water)

    # BẬC THANG ĐÁ ĐI XUỐNG AO NGÀY XƯA (Thay thế cầu ao cũ)
    # Bờ hè đại lộ ở Z = +0.05m
    add_box("BoHe_CauAoDa", (4.82, 17.2, 0.0), (0.18, 1.60, 0.08), mat_blue_stone)
    # Bậc 1 (trên cạn): Đỉnh Z = +0.02m, dày 0.06m
    add_box("BacThangDa_1", (4.50, 17.3, -0.02), (0.35, 1.40, 0.07), mat_blue_stone)
    # Bậc 2 (nước đến tầm giữa bậc 2!): Đỉnh Z = -0.04m, đáy Z = -0.12m, nước Z = -0.08m!
    add_box("BacThangDa_2", (4.15, 17.3, -0.12), (0.35, 1.40, 0.08), mat_wash_stone)
    # Bậc 3 (ngập dưới nước): Đỉnh Z = -0.12m, đáy Z = -0.22m
    add_box("BacThangDa_3", (3.80, 17.3, -0.22), (0.35, 1.40, 0.10), mat_blue_stone)
    # Cọc tre vịn tay ngày xưa cắm nghiêng cạnh bậc thang
    add_cylinder("CocTre_VinTay_Ao", (4.15, 17.15, -0.65), 0.04, 1.55, mat_bamboo)
    # Phiến đá giặt đồ, thau đồng và chày đập vải ở bậc thang
    add_box("PhienDa_GiatDo_Bac2", (4.18, 18.15, -0.04), (0.30, 0.45, 0.04), mat_wash_stone)
    add_cylinder("ThauDong_GiatDo_Day", (4.25, 17.55, -0.03), 0.16, 0.02, mat_wash_tub)
    add_cylinder("ThauDong_GiatDo_Vanh", (4.25, 17.55, -0.01), 0.18, 0.09, mat_wash_tub, vertices=16)
    add_cylinder("ChayDap_GiatDo", (4.35, 17.90, 0.01), 0.025, 0.32, mat_wood_dark)

    # Đàn cá chép đồng bơi lội trong ao 6x5
    carp_data = [
        ("CaChep_Bac1",    (2.4, 16.5, -0.12), 55.0,   0.85, mat_carp_silver, mat_carp_fin),
        ("CaChep_VangDong",(3.4, 17.0, -0.11), -40.0,  0.90, mat_carp_gold,   mat_carp_fin),
        ("CaChep_Bac2",    (2.0, 18.2, -0.13), 125.0,  0.80, mat_carp_silver, mat_carp_fin),
        ("CaChep_DoQue1",  (3.8, 18.0, -0.12), -75.0,  0.75, mat_carp_red,    mat_carp_fin),
        ("CaChep_Dong3",   (1.6, 19.5, -0.13), 15.0,   0.82, mat_carp_silver, mat_carp_fin),
        ("CaChep_Vang2",   (3.2, 19.8, -0.12), -120.0, 0.85, mat_carp_gold,   mat_carp_fin),
        ("CaChep_DoQue2",  (2.5, 20.2, -0.13), 85.0,   0.78, mat_carp_red,    mat_carp_fin),
    ]
    for c_name, c_loc, c_yaw, c_sc, c_mb, c_mf in carp_data:
        add_carp_fish(c_name, c_loc, c_yaw, c_sc, c_mb, c_mf)

    add_light_source("Light_AoCa_Fill", (2.5, 18.0, 0.25), energy=40.0, color=(0.92, 0.98, 0.95))

    # Cụm hoa sen & hoa súng nổi trên mặt ao
    lotus_clusters = [
        ("Sen_Cum1", (1.2, 16.2, -0.07)),
        ("Sen_Cum2", (3.8, 19.8, -0.07)),
        ("Sen_Cum3", (1.2, 19.5, -0.07)),
        ("Sen_Cum4", (2.8, 15.8, -0.07))
    ]
    for c_name, c_pos in lotus_clusters:
        add_lotus_cluster(c_name, c_pos, mat_lotus_leaf, mat_lotus_pink, mat_lotus_yellow)

    # 5. KHOẢNG CÁCH 1M GIỮA AO CÁ VÀ CĂN 3 (Y = 21.0 -> 22.0m)
    add_box("SanDem_AoCa_Nha3", (0.0, 21.0, 0.01), (5.0, 1.0, 0.04), mat_grass)
    add_cylinder("DaBuoc_Dem2_1", (1.8, 21.5, 0.04), 0.25, 0.03, mat_blue_stone)
    add_cylinder("DaBuoc_Dem2_2", (3.2, 21.5, 0.04), 0.25, 0.03, mat_blue_stone)
    add_cylinder("BuiHoa_Dem2_1", (0.8, 21.5, 0.04), 0.20, 0.35, mat_flower_pur)
    add_cylinder("BuiHoa_Dem2_2", (4.4, 21.5, 0.04), 0.20, 0.35, mat_flower_red)

    # 6. CĂN 3 (6x4, Y = 22.0 -> 28.0m): Nhà nghỉ view ao và view vườn hoa
    build_custom_house_6x4("NhaKhach3_6x4", 22.0, door_pos="left", wc_pos="north", room_type="view_ao")

    # 7. CÁI VƯỜN RÚT GỌN 9M (Y = 28.0 -> 37.0m, Rộng 5.0m = 45 m²)
    # BỐ CỤC CHUẨN XÁC: MẶT TRƯỚC CỦA VƯỜN ĐỐI DIỆN TRỰC TIẾP VỚI NHÀ 3 GIAN BẮC BỘ!
    # - Mặt trước nằm tại X = 5.0m (chạy dọc từ Y = 28.0 -> 37.0m đối diện Nhà 3 Gian qua đại lộ 8m)
    # - Mặt trước có HÀNG RÀO BỤI HOA CAO 70CM chạy dọc mép đại lộ, có LỐI ĐI VÀO Ở GIỮA
    # - Phần trước vườn hai bên lối vào TRỒNG HOA 2 BÊN rực rỡ
    # - Nhìn vào từ lối đi (hướng Tây từ X = 5.0m vào sâu trong vườn):
    #   + BÊN TRÁI (phía Nam Y: 28.0 -> 32.0m): TRỒNG CÂY ĂN TRÁI (Bưởi Diễn, Khế ngọt, Mộc hương)
    #   + BÊN PHẢI (phía Bắc Y: 33.2 -> 37.0m): TRỒNG RAU SẠCH (các luống cải, muống, giàn mướp)
    #   + CUỐI GẦN DÃY TƯỜNG BÊN PHẢI VƯỜN (X: 0.4 -> 2.2m, Y: 34.6 -> 36.8m): CHUỒNG GÀ QUÊ!
    
    # Thảm cỏ nền toàn bộ khu vườn 9m (X: 0.0 -> 5.0m, Y: 28.0 -> 37.0m)
    add_box("ThamCo_Vuon9m", (0.0, 28.0, 0.01), (5.0, 9.0, 0.03), mat_grass)

    # A. MẶT TIỀN VƯỜN: HÀNG RÀO BỤI HOA CAO 70CM TẠI X = 5.0M (ĐỐI DIỆN NHÀ 3 GIAN)
    # 1. Đoạn rào hoa bên trái lối vào (Y: 28.0 -> 32.0m, dài 4.0m, cao 0.70m)
    add_box("HangRaoHoa_MatTien_Nam", (4.70, 28.0, 0.02), (0.30, 4.0, 0.65), mat_grass)
    for ifl in range(10):
        fy = 28.20 + ifl * 0.40
        add_sphere(f"HoaRao_Nam_{ifl}", (4.85, fy, 0.68), radius=0.10, material=mat_flower_red if ifl % 2 == 0 else mat_flower_ylw)

    # 2. Đoạn rào hoa bên phải lối vào (Y: 33.2 -> 37.0m, dài 3.8m, cao 0.70m)
    add_box("HangRaoHoa_MatTien_Bac", (4.70, 33.2, 0.02), (0.30, 3.8, 0.65), mat_grass)
    for ifl in range(9):
        fy = 33.40 + ifl * 0.40
        add_sphere(f"HoaRao_Bac_{ifl}", (4.85, fy, 0.68), radius=0.10, material=mat_flower_pur if ifl % 2 == 0 else mat_flower_ylw)

    # B. ĐƯỜNG ĐI VÀO VƯỜN Ở GIỮA MẶT TIỀN (Từ X = 5.0m vào sâu X = 0.5m, tại Y ~ 32.6m)
    # Lối đi dạo lát đá sa thạch tự nhiên bước vào vườn
    garden_path_x = [4.8, 4.2, 3.6, 3.0, 2.4, 1.8, 1.2, 0.6]
    for idx, px in enumerate(garden_path_x):
        add_cylinder(f"DaLoiDiVuon_{idx}", (px, 32.6, 0.03), 0.28, 0.03, mat_blue_stone)

    # C. HOA TRỒNG 2 BÊN PHẦN TRƯỚC LỐI ĐI VÀO (X: 3.6 -> 4.7m)
    # Bồn hoa bên trái lối vào (phía Nam: Y = 30.8 -> 32.0m)
    add_box("BonHoa_Truoc_Trai", (3.6, 30.8, 0.02), (1.1, 1.2, 0.15), mat_soil)
    for ih in range(6):
        hx = 3.8 + (ih % 3) * 0.40
        hy = 31.0 + (ih // 3) * 0.50
        add_sphere(f"HoaBon_Trai_{ih}", (hx, hy, 0.28), radius=0.12, material=mat_flower_red if ih % 2 == 0 else mat_flower_ylw)

    # Bồn hoa bên phải lối vào (phía Bắc: Y = 33.2 -> 34.4m)
    add_box("BonHoa_Truoc_Phai", (3.6, 33.2, 0.02), (1.1, 1.2, 0.15), mat_soil)
    for ih in range(6):
        hx = 3.8 + (ih % 3) * 0.40
        hy = 33.4 + (ih // 3) * 0.50
        add_sphere(f"HoaBon_Phai_{ih}", (hx, hy, 0.28), radius=0.12, material=mat_flower_pur if ih % 2 == 0 else mat_flower_ylw)

    # D. NHÌN VÀO TỪ LỐI ĐI: BÊN TRÁI TRỒNG CÂY ĂN TRÁI (Phía Nam Y: 28.0 -> 32.0m, X: 0.0 -> 4.5m)
    # 1. Cây Bưởi Diễn trĩu quả vàng óng
    add_grapefruit_tree("CayBuoi_VuonTrai", (2.0, 29.8, 0.0), trunk_r=0.15, height=3.4, mat_wood=mat_wood_dark, mat_leaf=mat_grass, mat_fruit=mat_lotus_yellow)
    # 2. Cây Khế Ngọt hoa tím trĩu cành
    add_tree("CayKhe_VuonTrai", (3.6, 29.4, 0.0), 0.16, 3.3, 1.5, mat_wood_dark, mat_grass)
    # 3. Cây Hoa Mộc Hương ngát hương
    add_tree("CayMoc_VuonTrai", (1.0, 31.0, 0.0), 0.14, 3.0, 1.3, mat_wood_dark, mat_grass)
    # Thảm hoa cỏ nhung dưới tán cây
    for ift in range(4):
        tx = 1.2 + (ift % 2) * 1.5
        ty = 28.6 + (ift // 2) * 1.6
        add_cylinder(f"Khombuicay_Trai_{ift}", (tx, ty, 0.02), 0.25, 0.25, mat_grass)

    # E. NHÌN VÀO TỪ LỐI ĐI: BÊN PHẢI TRỒNG RAU (Phía Bắc Y: 33.2 -> 37.0m, X: 2.2 -> 4.6m)
    # 1. Luống rau cải xanh 1: Y = 33.8 -> 35.1m, X: 2.5 -> 4.6m
    add_box("LuongDat_Rau1", (2.5, 33.8, 0.02), (2.1, 1.3, 0.14), mat_soil)
    for ir in range(12):
        rx = 2.7 + (ir % 4) * 0.50
        ry = 34.0 + (ir // 4) * 0.45
        add_cylinder(f"CayRauCai_{ir}", (rx, ry, 0.16), 0.12, 0.14, mat_veggie)

    # 2. Luống rau muống / mồng tơi 2: Y = 35.5 -> 36.8m, X: 2.5 -> 4.6m
    add_box("LuongDat_Rau2", (2.5, 35.5, 0.02), (2.1, 1.3, 0.14), mat_soil)
    for ir in range(12):
        rx = 2.7 + (ir % 4) * 0.50
        ry = 35.7 + (ir // 4) * 0.45
        add_cylinder(f"CayRauMuong_{ir}", (rx, ry, 0.16), 0.11, 0.15, mat_grass)

    # 3. Giàn mướp / bầu hoa vàng leo giàn tre bên cạnh luống rau
    add_cylinder("GianTre_Cot1", (2.4, 33.8, 0.02), 0.035, 1.70, mat_bamboo)
    add_cylinder("GianTre_Cot2", (2.4, 36.8, 0.02), 0.035, 1.70, mat_bamboo)
    add_box("GianTre_XaNgang", (2.38, 33.8, 1.65), (0.05, 3.0, 0.04), mat_bamboo)

    # F. CUỐI GẦN DÃY TƯỜNG BÊN PHẢI VƯỜN: CHUỒNG GÀ (Góc cuối Bắc-Tây: X: 0.4 -> 2.2m, Y: 34.6 -> 36.8m)
    # Nền đất cát chuồng gà
    add_box("NenDat_ChuongGa", (0.4, 34.6, 0.02), (1.8, 2.2, 0.05), mat_soil)
    # 4 Cột trụ chuồng gà gỗ tre
    for (cx, cy) in [(0.45, 34.65), (2.15, 34.65), (0.45, 36.75), (2.15, 36.75)]:
        add_cylinder(f"Cot_ChuongGa_{cx}_{cy}", (cx, cy, 0.02), 0.05, 1.60, mat_chicken_coop)
    # Khung xà giằng chuồng gà
    add_box("Xa_ChuongGa_Duoi", (0.45, 34.65, 0.05), (1.70, 2.10, 0.06), mat_chicken_coop)
    add_box("Xa_ChuongGa_Giua", (0.45, 34.65, 0.75), (1.70, 2.10, 0.05), mat_chicken_coop)
    add_box("Xa_ChuongGa_Tren", (0.45, 34.65, 1.55), (1.70, 2.10, 0.06), mat_chicken_coop)
    # Lưới mắt cáo bao quanh chuồng gà
    add_box("Luoi_ChuongGa_Truoc", (2.12, 34.68, 0.06), (0.02, 2.05, 1.48), mat_wire_mesh)
    add_box("Luoi_ChuongGa_Nam",   (0.48, 34.68, 0.06), (1.64, 0.02, 1.48), mat_wire_mesh)
    # Mái che chuồng gà lợp ngói đỏ dốc
    add_gabled_roof("Mai_ChuongGa", 0.35, 2.25, 34.5, 36.9, 1.55, 1.95, overhang=0.15, material=mat_roof_red)

    # Nội thất chuồng gà:
    # Ổ rơm cho gà đẻ trứng
    add_cylinder("ORom_DeTrung_1", (0.9, 36.3, 0.08), 0.25, 0.12, mat_straw)
    add_cylinder("ORom_DeTrung_2", (1.6, 36.3, 0.08), 0.25, 0.12, mat_straw)
    # Vài quả trứng gà quê trắng hồng
    add_sphere("TrungGa_1", (0.90, 36.30, 0.18), radius=0.035, scale=(0.85, 0.85, 1.15), material=mat_white_linen)
    add_sphere("TrungGa_2", (1.58, 36.28, 0.18), radius=0.035, scale=(0.85, 0.85, 1.15), material=mat_white_linen)
    # Sào tre cho gà đậu ngủ
    add_cylinder("SaoTre_GaDau", (1.3, 35.5, 0.55), 0.035, 1.70, mat_bamboo)
    # Máng ăn tre & máng nước cho gà
    add_box("MangAn_ThocGa", (0.8, 34.9, 0.05), (0.80, 0.15, 0.08), mat_bamboo)
    add_cylinder("MangNuoc_GaUong", (1.8, 35.0, 0.05), 0.12, 0.08, mat_blue_stone)

    # Đàn gà thôn quê sinh động:
    # 1. Chú Gà Trống Thiến oai vệ (lông tía đỏ, mào cờ)
    add_sphere("GaTrong_Than", (1.1, 35.4, 0.22), radius=0.14, scale=(1.2, 0.85, 0.95), material=mat_chicken_body)
    add_sphere("GaTrong_Co",   (1.0, 35.25, 0.32), radius=0.07, scale=(0.8, 0.8, 1.3), material=mat_chicken_body)
    add_sphere("GaTrong_Dau",  (0.98, 35.20, 0.40), radius=0.055, material=mat_chicken_comb)
    add_cone("GaTrong_Mao",    (0.98, 35.20, 0.46), 0.03, 0.06, mat_chicken_comb)
    add_cone("GaTrong_Duoi",   (1.25, 35.60, 0.35), 0.08, 0.24, mat_chicken_body)

    # 2. Cô Gà Mái Mơ vàng ươm đang mổ thóc
    add_sphere("GaMai_Than", (1.7, 35.2, 0.18), radius=0.12, scale=(1.1, 0.8, 0.85), material=mat_chicken_gold)
    add_sphere("GaMai_Dau",  (1.65, 35.05, 0.18), radius=0.05, material=mat_chicken_gold)
    add_cone("GaMai_Mao",    (1.65, 35.05, 0.23), 0.02, 0.035, mat_chicken_comb)

    # Ánh sáng ấm cho khu vực Vườn & Chuồng Gà
    add_light_source("Light_Vuon_ChuongGa", (2.5, 33.0, 3.5), energy=35.0, color=(1.0, 0.96, 0.88))
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
    setup_camera("Cam_4_KyVat_NhaAn", (15.2, 3.8, 1.65), (17.5, 7.5, 1.45), focal_length=24)
    setup_camera("Cam_Bep_WC_Mo", (10.0, 1.2, 1.65), (15.2, 1.8, 1.35), focal_length=24)
    setup_camera("Cam_NhaAn_MaiLa", (10.2, 7.5, 1.65), (15.2, 7.5, 1.50), focal_length=24)

    # 5. Cận cảnh Ao Cá Quê nhìn từ hiên Căn Nhà 2
    setup_camera("Cam_5_ViewAo_PhongNgam", (4.8, 14.2, 1.5), (2.5, 18.0, 0.0), focal_length=24)

    # 6. Phối cảnh cổng chính mở rộng 8m nhìn sâu vào trục đại lộ
    setup_camera("Cam_6_CongChinh", (9.0, -7.5, 1.9), (9.0, 4.0, 1.6), focal_length=26)
    setup_camera("Cam_HangCau_Cong", (2.5, -4.5, 1.75), (2.5, 2.5, 1.8), focal_length=24)

    # 7. Cận cảnh 2 Căn Nhà 6x4 và Ao Cá Dãy Trái
    setup_camera("Cam_7_HanhLang_NhaKhach", (5.8, 1.2, 1.9), (3.0, 14.0, 1.2), focal_length=26)

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

    # 13. CẬN CẢNH VƯỜN RAU, CÂY ĂN TRÁI & CHUỒNG GÀ (Y = 28 -> 37m)
    setup_camera("Cam_12_VuonRau_ChuongGa", (8.5, 32.6, 1.75), (2.0, 33.5, 1.20), focal_length=24)

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
