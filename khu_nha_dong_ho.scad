// ==============================================================================
// DỰ ÁN QUY HOẠCH KIẾN TRÚC KHU NHÀ DÒNG HỌ (37.0m x 18.0m = 666m²)
// BẢN MÔ PHỎNG 3D THỰC THỂ CHO OPENSCAD (Bản Hoàn Thiện Chuẩn CAD)
// Đơn vị đo trong mô hình: 1 unit = 1 mét (1.0m)
// Hệ tọa độ:
//   X: Chiều ngang 18m (X = 0: Ranh đất Trái; X = 18: Ranh đất Phải)
//   Y: Chiều sâu 37m   (Y = 0: Cổng chính;    Y = 37: Cuối khu đất)
//   Z: Chiều cao công trình
// ==============================================================================

/* [TÙY CHỌN HIỂN THỊ TRỰC QUAN] */
show_roofs      = true;     // Đổi thành false để BỎ MÁI, xem nội thất và dải kỷ vật
show_trees      = true;     // Bật/Tắt cây xanh sân vườn
show_furniture  = true;     // Bật/Tắt nội thất bàn ghế, cối xay, cối giã
show_signs      = true;     // Bật/Tắt biển chỉ dẫn phân khu

$fn = 36; // Độ mượt đường tròn

// BẢNG MÀU CHUẨN KIẾN TRÚC
C_ROAD      = [0.28, 0.31, 0.36];  // Đá bazan lát đường
C_WALL      = [0.93, 0.91, 0.86];  // Tường trắng kem
C_WOOD      = [0.48, 0.24, 0.08];  // Gỗ lim già
C_ROOF_RED  = [0.82, 0.20, 0.12];  // Ngói đỏ mũi hài
C_ROOF_PAV  = [0.55, 0.22, 0.68];  // Mái đài lục giác
C_STONE     = [0.78, 0.78, 0.76];  // Đá xanh lát sân
C_WATER     = [0.12, 0.62, 0.85, 0.75]; // Nước ao trong xanh
C_GLASS     = [0.45, 0.78, 0.92, 0.30]; // Vách kính cường lực
C_GRASS     = [0.32, 0.68, 0.28];  // Cỏ sân vườn
C_GOLD      = [0.96, 0.78, 0.12];  // Sơn son thếp vàng
C_PEBBLE    = [0.95, 0.95, 0.92];  // Sỏi trắng rải dải kỷ vật

// ------------------------------------------------------------------------------
// MODULE TOÀN CẢNH KHUÔN VIÊN
// ------------------------------------------------------------------------------
module KhuNhaDongHo() {
    GroundBase();
    BoundaryWalls();
    CentralRoad();
    
    // DÃY BÊN PHẢI (Khu 3: 13.5m -> Khu 2: 12.0m -> Khu 1: 11.5m)
    RightWing();
    
    // DÃY BÊN TRÁI (Khu 4: 12.0m -> Khu 5: 5.0m -> Khu 6: 16.0m -> Khu 7: 4.0m)
    LeftWing();
    
    if (show_signs) {
        AllSignboards();
    }
}

// ------------------------------------------------------------------------------
// 1. ĐẤT NỀN VÀ TƯỜNG BAO
// ------------------------------------------------------------------------------
module GroundBase() {
    // Nền đất vườn ngoại vi
    color([0.22, 0.48, 0.20])
    translate([-2.5, -3.0, -0.3])
    cube([18 + 5, 37 + 5.5, 0.3]);

    // Mặt bằng khuôn viên nội bộ lát đá
    color([0.88, 0.87, 0.83])
    translate([0, 0, -0.05])
    cube([18, 37, 0.05]);
}

module BoundaryWalls() {
    h_wall = 2.2;
    t_wall = 0.2;
    
    color(C_WALL) {
        // Tường ranh bên Trái (X = 0)
        translate([-t_wall, 0, 0]) cube([t_wall, 37, h_wall]);
        // Tường ranh bên Phải (X = 18)
        translate([18, 0, 0]) cube([t_wall, 37, h_wall]);
        // Tường ranh Cuối đất (Y = 37)
        translate([-t_wall, 37, 0]) cube([18 + 2*t_wall, t_wall, h_wall]);
        // Tường mặt tiền bên Trái (X: 0 -> 7)
        translate([-t_wall, -t_wall, 0]) cube([7 + t_wall, t_wall, h_wall]);
        // Tường mặt tiền bên Phải (X: 11 -> 18)
        translate([11, -t_wall, 0]) cube([7 + t_wall, t_wall, h_wall]);
    }
    
    // Mũ tường ngói đỏ chạy viền trên tường bao
    color(C_ROOF_RED) {
        translate([-t_wall - 0.05, -t_wall, h_wall]) cube([t_wall + 0.1, 37 + t_wall, 0.08]);
        translate([18 - 0.05, -t_wall, h_wall]) cube([t_wall + 0.1, 37 + t_wall, 0.08]);
        translate([-t_wall, 37 - 0.05, h_wall]) cube([18 + 2*t_wall, t_wall + 0.1, 0.08]);
    }

    // CỔNG CHÍNH TAM QUAN TRỤ BIỂU (X = 7 -> 11, Y = 0)
    color([0.70, 0.70, 0.72]) {
        // 2 Cột trụ cổng đá bazan nguyên khối
        translate([7 - 0.3, -0.35, 0]) cube([0.6, 0.6, 4.0]);
        translate([11 - 0.3, -0.35, 0]) cube([0.6, 0.6, 4.0]);
        
        // Đỉnh búp sen trụ cổng
        translate([7, -0.05, 4.0]) cylinder(r1=0.4, r2=0.08, h=0.7);
        translate([11, -0.05, 4.0]) cylinder(r1=0.4, r2=0.08, h=0.7);
        
        // Xà ngang cổng
        translate([7, -0.2, 3.3]) cube([4.0, 0.35, 0.45]);
    }
    // Biển đại tự cổng chính
    color([0.75, 0.12, 0.10])
    translate([7.8, -0.25, 3.35])
    cube([2.4, 0.06, 0.35]);
}

module CentralRoad() {
    // Trục đường chính rộng 4.0m kéo dài suốt 37m
    color(C_ROAD)
    translate([7, 0, 0.01])
    cube([4, 37, 0.04]);
    
    // Vạch sơn chỉ dẫn tim đường
    color([0.95, 0.85, 0.20])
    for (y = [1.5 : 3.5 : 35.5]) {
        translate([8.95, y, 0.055])
        cube([0.1, 2.0, 0.005]);
    }
    
    // Bó vỉa đá xám 2 bên trục đường
    color([0.65, 0.65, 0.65]) {
        translate([6.9, 0, 0]) cube([0.1, 37, 0.08]);
        translate([11.0, 0, 0]) cube([0.1, 37, 0.08]);
    }
}

// ------------------------------------------------------------------------------
// 2. DÃY BÊN PHẢI (Khu 3, Khu 2, Khu 1)
// ------------------------------------------------------------------------------
module RightWing() {
    // Dải thụt lùi 1.0m ven tường ngoài (X = 17 -> 18, Y = 0 -> 37)
    color([0.82, 0.80, 0.75])
    translate([17, 0, 0.005])
    cube([1, 37, 0.02]);
    
    // KHU 3: Bếp, 2 WC, Nhà Ăn & Hành lang kỷ vật (Y = 0 -> 13.5)
    Khu3();

    // KHU 2: Đài Lục Giác đường kính 6.0m & 2 bên sân thoáng (Y = 13.5 -> 25.5)
    Khu2();

    // KHU 1: Nhà 3 Gian Bắc Bộ, hè 9m, vườn hồng, chuối, toilet & lối 1m (Y = 25.5 -> 37.0)
    Khu1();
}

// KHU 3 CHI TIẾT
module Khu3() {
    // --- 1. Cụm Bếp & 2 WC (Y = 0 -> 3.0, dài 3m ở phía cổng) ---
    // 2 WC xây trực tiếp sát tường bao ranh đất (X = 16.5 -> 18.0, Y = 0 -> 3.0)
    color([0.86, 0.88, 0.92]) {
        difference() {
            translate([16.5, 0, 0]) cube([1.5, 3.0, 2.7]);
            // Buồng WC 1 & 2 rỗng suốt trần
            translate([16.65, 0.15, 0.1]) cube([1.2, 1.2, 3.0]);
            translate([16.65, 1.65, 0.1]) cube([1.2, 1.2, 3.0]);
            // Cửa WC
            translate([16.45, 0.4, 0]) cube([0.2, 0.7, 2.1]);
            translate([16.45, 1.9, 0]) cube([0.2, 0.7, 2.1]);
        }
    }

    // Bếp nấu cỗ (X = 11.0 -> 16.5, Y = 0 -> 3.0, rộng 5.5m x dài 3m)
    color(C_WALL) {
        difference() {
            translate([11.0, 0, 0]) cube([5.5, 3.0, 3.2]);
            translate([11.2, 0.2, 0]) cube([5.1, 2.6, 3.5]);
            // Cửa ra đường 4m
            translate([11.8, -0.05, 0]) cube([1.0, 0.3, 2.2]);
            // Cửa sổ mặt tiền
            translate([13.4, -0.05, 1.1]) cube([2.0, 0.3, 1.1]);
            // Cửa thông nội bộ sang Nhà Ăn
            translate([13.5, 2.9, 0]) cube([1.2, 0.3, 2.2]);
        }
    }
    // Bàn đảo soạn cỗ & bếp nấu
    if (show_furniture) {
        color([0.75, 0.78, 0.82]) {
            translate([12.5, 1.2, 0]) cube([2.5, 0.8, 0.85]);
            translate([15.5, 0.3, 0]) cube([0.7, 2.0, 0.85]);
        }
    }
    // Mái cụm Bếp & WC
    if (show_roofs) {
        color(C_ROOF_RED)
        translate([10.8, -0.2, 3.2])
        cube([7.4, 3.4, 0.35]);
    }

    // --- 2. Nhà Ăn Gia Tộc (X = 11.0 -> 17.0, Y = 3.0 -> 13.5, rộng 6m x dài 10.5m = 63m²) ---
    color(C_WALL) {
        // Tường đầu giáp bếp & tường cuối giáp Khu 2
        translate([11, 3.0, 0]) cube([6.0, 0.18, 3.5]);
        translate([11, 13.32, 0]) cube([6.0, 0.18, 3.5]);
        // Cột đỡ chịu lực mặt tiền đường
        for (y = [3.0 : 2.6 : 13.5]) {
            translate([11, y - 0.1, 0]) cube([0.22, 0.22, 3.5]);
        }
    }

    // Hệ vách kính xếp trượt mặt tiền đường 4m (X = 11)
    color(C_GLASS)
    translate([11.05, 3.2, 0])
    cube([0.05, 10.0, 3.3]);

    // HỆ VÁCH KÍNH CƯỜNG LỰC NHÌN SANG HÀNH LANG KỶ VẬT (X = 17, Y = 3.0 -> 13.5)
    color(C_GLASS)
    translate([16.95, 3.2, 0])
    cube([0.05, 10.0, 3.3]);
    
    // Nẹp khung kính nhôm xingfa
    color([0.2, 0.2, 0.2]) {
        for (y = [3.0 : 2.1 : 13.5]) {
            translate([16.92, y, 0]) cube([0.1, 0.08, 3.5]);
        }
    }

    // BÀN ĂN THÔNG MINH BIẾN HÌNH Ở TRUNG TÂM NHÀ ĂN
    if (show_furniture) {
        color(C_WOOD) {
            translate([14.0, 8.25, 0.75])
            resize([2.2, 5.2, 0.08])
            cylinder(r=2.5, h=0.08);

            translate([14.0, 6.5, 0]) cylinder(r=0.25, h=0.75);
            translate([14.0, 10.0, 0]) cylinder(r=0.25, h=0.75);
        }
        color([0.65, 0.38, 0.18]) {
            for (i = [0 : 5]) {
                translate([12.5, 5.8 + i*0.95, 0]) cube([0.42, 0.42, 0.45]);
                translate([15.1, 5.8 + i*0.95, 0]) cube([0.42, 0.42, 0.45]);
            }
        }
    }

    // Mái Nhà Ăn
    if (show_roofs) {
        color(C_ROOF_RED) {
            translate([10.7, 2.9, 3.5])
            cube([6.6, 10.7, 0.4]);
        }
    }

    // --- 3. HÀNH LANG KỶ VẬT XƯA TRONG DẢI LÙI 1M (X = 17.0 -> 18.0, Y = 3.0 -> 13.5) ---
    // Nền rải sỏi trắng cuội suối
    color(C_PEBBLE)
    translate([17.02, 3.0, 0.02])
    cube([0.96, 10.5, 0.04]);

    if (show_furniture) {
        // CỐI XAY THÓC CỔ TRUYỀN BẮC BỘ (Y = 6.2)
        translate([17.5, 6.2, 0.06]) {
            color([0.72, 0.52, 0.32]) cylinder(r=0.40, h=0.48);
            color([0.65, 0.45, 0.28]) translate([0, 0, 0.48]) cylinder(r=0.36, h=0.36);
            color([0.42, 0.28, 0.12]) {
                translate([-0.1, 0, 0.72]) rotate([0, 25, 45]) cube([0.06, 0.06, 0.95]);
            }
        }

        // Bụi trúc kiểng phân cách (Y = 8.25)
        if (show_trees) {
            color([0.15, 0.62, 0.20]) {
                translate([17.5, 8.0, 0]) cylinder(r=0.03, h=2.6);
                translate([17.65, 8.3, 0]) cylinder(r=0.035, h=2.8);
                translate([17.38, 8.55, 0]) cylinder(r=0.03, h=2.5);
                translate([17.5, 8.25, 2.0]) sphere(r=0.45);
            }
        }

        // CỐI GIÃ GẠO BẰNG CẦN ĐẠP CHÂN (Y = 10.5)
        translate([17.5, 10.5, 0.06]) {
            color([0.50, 0.55, 0.60]) {
                difference() {
                    translate([0, -0.9, 0]) cylinder(r=0.35, h=0.48);
                    translate([0, -0.9, 0.26]) cylinder(r=0.24, h=0.25);
                }
            }
            color([0.48, 0.28, 0.12]) translate([-0.15, 0, 0]) cube([0.3, 0.12, 0.52]);
            color([0.55, 0.35, 0.18]) {
                translate([-0.05, -1.0, 0.42]) cube([0.1, 2.1, 0.1]);
                translate([-0.04, -0.9, 0.16]) cube([0.08, 0.08, 0.32]);
                translate([-0.16, 0.95, 0.46]) cube([0.32, 0.22, 0.06]);
            }
        }
    }
}

// KHU 2 CHI TIẾT: Đài Lục Giác đường kính đủ 6.0m (X = 11 -> 17, tâm Y = 19.5)
module Khu2() {
    x_c = 14.0;
    y_c = 19.5;
    r_lucgiac = 3.0; // Đường kính = 6.0m

    // Sân trước (Y: 13.5 -> 16.5) & Sân sau (Y: 22.5 -> 25.5) thoáng đón gió
    color([0.90, 0.88, 0.84]) {
        translate([11, 13.5, 0.01]) cube([6.0, 3.0, 0.02]);
        translate([11, 22.5, 0.01]) cube([6.0, 3.0, 0.02]);
    }

    // ĐÀI LỤC GIÁC 6.0M
    color([0.76, 0.76, 0.74])
    translate([x_c, y_c, 0])
    cylinder(r=r_lucgiac, h=0.35, $fn=6);
    
    color([0.65, 0.38, 0.20])
    translate([x_c, y_c, 0.35])
    cylinder(r=r_lucgiac - 0.15, h=0.08, $fn=6);

    // 6 Cột gỗ lim xung quanh
    color(C_WOOD) {
        for (i = [0 : 5]) {
            ang = i * 60 + 30;
            px = x_c + (r_lucgiac - 0.35) * cos(ang);
            py = y_c + (r_lucgiac - 0.35) * sin(ang);
            translate([px, py, 0.4]) cylinder(r=0.13, h=3.0);
        }
    }

    // Lan can và ghế tựa quanh các cạnh (mở 1 cạnh đón khách)
    color([0.58, 0.32, 0.15]) {
        for (i = [1 : 5]) {
            ang1 = i * 60 + 30;
            ang2 = (i+1) * 60 + 30;
            x1 = x_c + (r_lucgiac - 0.35) * cos(ang1);
            y1 = y_c + (r_lucgiac - 0.35) * sin(ang1);
            x2 = x_c + (r_lucgiac - 0.35) * cos(ang2);
            y2 = y_c + (r_lucgiac - 0.35) * sin(ang2);
            
            translate([(x1+x2)/2, (y1+y2)/2, 0.9])
            rotate([0, 0, ang1 + 60])
            cube([2.6, 0.08, 0.1], center=true);
            
            translate([(x1+x2)/2, (y1+y2)/2, 0.5])
            rotate([0, 0, ang1 + 60])
            cube([2.6, 0.35, 0.06], center=true);
        }
    }

    // Bàn trà lục giác ở tâm đài
    if (show_furniture) {
        color(C_WOOD) {
            translate([x_c, y_c, 0.4]) cylinder(r=0.75, h=0.75, $fn=6);
            for (i = [0 : 5]) {
                ang = i * 60;
                translate([x_c + 1.35*cos(ang), y_c + 1.35*sin(ang), 0.4])
                cylinder(r=0.22, h=0.45);
            }
        }
    }

    // MÁI 2 TẦNG CHỒNG DIÊM (THEO MẪU FERINO)
    if (show_roofs) {
        // Tầng mái 1
        color(C_ROOF_PAV)
        translate([x_c, y_c, 3.2])
        cylinder(r1=3.45, r2=1.9, h=1.0, $fn=6);

        // Cổ diêm thông gió tầng giữa
        color([0.92, 0.88, 0.78])
        translate([x_c, y_c, 4.15])
        cylinder(r=1.7, h=0.4, $fn=6);

        // Tầng mái 2
        color(C_ROOF_PAV)
        translate([x_c, y_c, 4.5])
        cylinder(r1=2.05, r2=0.1, h=1.4, $fn=6);

        // Đỉnh hồ lô đồng
        color(C_GOLD)
        translate([x_c, y_c, 5.85])
        cylinder(r1=0.16, r2=0.02, h=0.55);
    }
}

// KHU 1 CHI TIẾT: Nhà 3 Gian Bắc Bộ (5m x 9m)
module Khu1() {
    // 1. Cái Hè 9m sát đường 4m (X = 11.0 -> 12.0, Y = 25.5 -> 34.5)
    color([0.82, 0.32, 0.20])
    translate([11.0, 25.5, 0.02])
    cube([1.0, 9.0, 0.3]);
    
    // Bậc tam cấp đá xanh dẫn lên hè
    color([0.68, 0.68, 0.68]) {
        translate([10.7, 28.5, 0]) cube([0.3, 3.0, 0.1]);
        translate([10.85, 28.5, 0.1]) cube([0.15, 3.0, 0.1]);
    }

    // 4 Cột hiên gỗ lim trên hè
    for (y = [25.8, 28.8, 31.8, 34.2]) {
        color([0.62, 0.62, 0.62])
        translate([11.5, y, 0.3]) cylinder(r=0.16, h=0.15);
        color(C_WOOD)
        translate([11.5, y, 0.45]) cylinder(r=0.12, h=2.85);
    }

    // 2. Nhà 3 Gian (X = 12.0 -> 17.0, Y = 25.5 -> 34.5, Rộng 5m x Dài 9m)
    color(C_WALL) {
        translate([12.0, 25.5, 0]) cube([5.0, 0.2, 3.5]);
        translate([12.0, 34.3, 0]) cube([5.0, 0.2, 3.5]);
        translate([16.8, 25.5, 0]) cube([0.2, 9.0, 3.5]);
        translate([12.2, 28.5, 0]) cube([4.6, 0.12, 3.2]);
        translate([12.2, 31.5, 0]) cube([4.6, 0.12, 3.2]);
    }

    // 3 Bộ Cửa Bức Bàn gỗ lim chạm khắc nhìn ra hè
    color([0.48, 0.22, 0.08]) {
        for (y = [26.0, 29.0, 32.0]) {
            translate([12.0, y, 0.3]) cube([0.1, 2.0, 2.7]);
        }
    }

    // Nội thất Gian giữa: Ban thờ tổ sơn son thếp vàng & Bộ trường kỷ tiếp khách
    if (show_furniture) {
        color(C_GOLD) {
            translate([15.4, 29.2, 0.3]) cube([1.2, 1.6, 1.2]);
            translate([16.65, 29.2, 2.4]) cube([0.08, 1.6, 0.4]);
        }
        color(C_WOOD) {
            translate([13.4, 26.5, 0.3]) cube([0.65, 1.6, 0.75]);
            translate([14.5, 26.5, 0.3]) cube([0.55, 1.6, 0.85]);
        }
    }

    // MÁI NHÀ 3 GIAN BẮC BỘ
    if (show_roofs) {
        color(C_ROOF_RED) {
            translate([10.5, 25.2, 3.3])
            rotate([0, -18, 0])
            cube([3.8, 9.6, 0.25]);

            translate([14.2, 25.2, 4.45])
            rotate([0, 18, 0])
            cube([3.5, 9.6, 0.25]);

            translate([14.1, 25.2, 4.45])
            cube([0.3, 9.6, 0.3]);
        }
        color([0.85, 0.85, 0.85]) {
            translate([14.1, 25.3, 4.75]) sphere(r=0.25);
            translate([14.1, 34.5, 4.75]) sphere(r=0.25);
        }
    }

    // 3. Cụm Kế Sát Nhà: Vườn Hồng, Bụi Chuối, Toilet (Y = 34.5 -> 36.0, dài 1.5m)
    color([0.92, 0.28, 0.48]) {
        translate([11.2, 34.6, 0.05]) cube([1.7, 1.2, 0.15]);
        for (x = [11.5, 12.0, 12.5]) {
            translate([x, 35.2, 0.35]) sphere(r=0.15);
        }
    }

    if (show_trees) {
        color([0.20, 0.65, 0.15]) {
            translate([13.8, 35.2, 0]) cylinder(r=0.1, h=1.8);
            translate([13.8, 35.2, 1.8]) sphere(r=0.6);
            translate([14.4, 35.4, 0]) cylinder(r=0.08, h=1.4);
            translate([14.4, 35.4, 1.4]) sphere(r=0.5);
        }
    }

    color(C_WALL) translate([15.0, 34.5, 0]) cube([2.0, 1.5, 2.6]);
    if (show_roofs) {
        color(C_ROOF_RED) translate([14.9, 34.4, 2.6]) cube([2.2, 1.7, 0.2]);
    }

    // 4. Đường Đi 1.0m Nối Ra Đường Chính (Y = 36.0 -> 37.0, X = 11 -> 18)
    color([0.76, 0.72, 0.68])
    translate([11.0, 36.0, 0.02])
    cube([7.0, 1.0, 0.04]);
}

// ------------------------------------------------------------------------------
// 3. DÃY BÊN TRÁI (Khu 4, Khu 5, Khu 6, Khu 7)
// ------------------------------------------------------------------------------
module LeftWing() {
    color([0.82, 0.80, 0.75])
    translate([0, 0, 0.005])
    cube([1, 37, 0.02]);

    // KHU 4: NHÀ KHÁCH 12M (X = 1 -> 7, Y = 0 -> 12.0)
    Khu4();

    // KHU 5: AO CÁ PHONG THỦY (X = 1 -> 7, Y = 12.0 -> 17.0)
    Khu5();

    // KHU 6: VƯỜN CÂY CẢNH QUAN (X = 1 -> 7, Y = 17.0 -> 33.0)
    Khu6();

    // KHU 7: QUỸ ĐẤT DỰ TRỮ (X = 1 -> 7, Y = 33.0 -> 37.0)
    Khu7();
}

// KHU 4: Nhà Khách (Rộng 6m x Dài 12m)
module Khu4() {
    color(C_WALL) {
        difference() {
            translate([1, 0, 0]) cube([6.0, 12.0, 3.4]);
            // Rỗng suốt trần để khi bỏ mái nhìn thấy rõ nội thất
            translate([1.2, 0.2, -0.1]) cube([5.6, 11.6, 4.0]);
            // Cửa chính vào nhà khách từ đường 4m
            translate([6.9, 1.5, 0]) cube([0.2, 1.2, 2.2]);
            // Cửa sổ các phòng ngủ nhìn ra đường
            translate([6.9, 5.5, 1.1]) cube([0.2, 1.8, 1.2]);
            // Cửa kính mở toang nhìn ra Ao Khu 5 (diện tường Y = 12)
            translate([1.3, 11.85, 0.2]) cube([5.4, 0.3, 3.0]);
        }
        
        // Vách ngăn Phần 1 (4m) & Phần 2 (4m) tại Y = 4.0
        translate([1.2, 4.0, 0]) cube([5.6, 0.15, 3.2]);
        // Vách ngăn Phần 2 & Phần 3 tại Y = 8.0
        translate([1.2, 8.0, 0]) cube([5.6, 0.15, 3.2]);
        // Vách ngăn tạo Phòng Ngắm Cảnh rộng cỡ 2m tại Y = 10.0
        translate([1.2, 10.0, 0]) cube([5.6, 0.15, 3.2]);
    }

    // HỆ VÁCH KÍNH LỚN VIEW TRỌN VẸN MẶT AO KHU 5 (Y = 12.0)
    color(C_GLASS)
    translate([1.3, 11.95, 0.1])
    cube([5.4, 0.05, 3.1]);

    if (show_furniture) {
        // Bàn trà & ghế bành thư giãn trong phòng ngắm cảnh 2m
        color(C_WOOD) {
            translate([4.0, 11.0, 0.35]) cylinder(r=0.6, h=0.45);
            translate([2.8, 10.7, 0.15]) cube([0.65, 0.65, 0.6]);
            translate([5.2, 10.7, 0.15]) cube([0.65, 0.65, 0.6]);
        }
        // Giường ngủ Phòng 1
        color([0.35, 0.48, 0.68]) translate([2.0, 1.5, 0.1]) cube([2.0, 1.8, 0.5]);
        // Giường ngủ Phòng 2
        color([0.35, 0.48, 0.68]) translate([2.0, 5.5, 0.1]) cube([2.0, 1.8, 0.5]);
    }

    // Mái Nhà Khách
    if (show_roofs) {
        color(C_ROOF_RED) {
            translate([0.8, -0.2, 3.4])
            cube([6.4, 12.4, 0.4]);
        }
    }
}

// KHU 5: Ao Cá Phong Thủy (Rộng 6m x Dài 5m = 30m²)
module Khu5() {
    color([0.55, 0.55, 0.52]) {
        difference() {
            translate([1.0, 12.0, -0.6]) cube([6.0, 5.0, 0.65]);
            translate([1.25, 12.25, -0.6]) cube([5.5, 4.5, 0.7]);
        }
    }
    
    color(C_WATER)
    translate([1.25, 12.25, -0.15])
    cube([5.5, 4.5, 0.05]);

    color([0.88, 0.32, 0.62]) {
        translate([2.5, 13.8, -0.12]) cylinder(r=0.38, h=0.08);
        translate([4.6, 15.2, -0.12]) cylinder(r=0.45, h=0.08);
        translate([3.3, 16.0, -0.12]) cylinder(r=0.32, h=0.08);
    }

    color(C_WOOD) {
        translate([3.5, 12.0, -0.05])
        cube([1.2, 1.8, 0.08]);
    }
}

// KHU 6: Vườn Cây Xanh Mát (Rộng 6m x Dài 16m = 96m²)
module Khu6() {
    color(C_GRASS)
    translate([1.0, 17.0, 0.01])
    cube([6.0, 16.0, 0.03]);

    color([0.75, 0.75, 0.72]) {
        for (y = [17.5 : 1.2 : 32.5]) {
            x_offset = 3.5 + 1.2 * sin(y * 40);
            translate([x_offset, y, 0.035])
            resize([0.9, 0.6, 0.02])
            cylinder(r=0.5, h=0.02);
        }
    }

    if (show_trees) {
        Tree([2.2, 19.5, 0], r_canopy=1.5, h_trunk=2.2, c_leaf=[0.24, 0.68, 0.20]);
        Tree([5.6, 21.2, 0], r_canopy=1.7, h_trunk=2.5, c_leaf=[0.18, 0.58, 0.18]);
        Tree([2.4, 25.5, 0], r_canopy=1.8, h_trunk=2.6, c_leaf=[0.22, 0.65, 0.22]);
        Tree([5.3, 28.5, 0], r_canopy=1.6, h_trunk=2.3, c_leaf=[0.20, 0.60, 0.20]);
        Tree([2.5, 31.5, 0], r_canopy=1.5, h_trunk=2.2, c_leaf=[0.25, 0.68, 0.22]);
    }
}

module Tree(pos, r_canopy=1.5, h_trunk=2.2, c_leaf=[0.2, 0.6, 0.2]) {
    translate(pos) {
        color([0.45, 0.28, 0.15])
        cylinder(r1=0.22, r2=0.15, h=h_trunk);
        
        color(c_leaf)
        translate([0, 0, h_trunk + r_canopy*0.7])
        sphere(r=r_canopy);
    }
}

// KHU 7: Quỹ Đất Dự Trữ (Rộng 6m x Dài 4m = 24m²)
module Khu7() {
    color([0.84, 0.82, 0.80])
    translate([1.0, 33.0, 0.01])
    cube([6.0, 4.0, 0.05]);

    color([0.65, 0.65, 0.65]) {
        translate([1.0, 33.0, 0.05]) cube([6.0, 0.15, 0.12]);
    }
}

// ------------------------------------------------------------------------------
// CỘT BIỂN CHỈ DẪN VEN ĐƯỜNG (STANDALONE SIGNPOSTS)
// ------------------------------------------------------------------------------
module SignPost(text_str, pos, rot_z=0, width_box=3.8) {
    translate(pos)
    rotate([0, 0, rot_z]) {
        // Cột đỡ inox/gỗ
        color([0.4, 0.4, 0.4])
        cylinder(r=0.06, h=1.6);
        
        // Bảng biển
        translate([-width_box/2, -0.04, 1.2]) {
            color([0.15, 0.22, 0.35])
            cube([width_box, 0.08, 0.55]);

            color([1.0, 0.85, 0.20])
            translate([0.15, -0.02, 0.12])
            rotate([90, 0, 0])
            linear_extrude(0.04) text(text_str, size=0.26, font="Arial:style=Bold");
        }
    }
}

module AllSignboards() {
    // Biển Cổng chính
    SignPost("CONG CHINH 4.0M", [9.0, -0.6, 0], rot_z=0, width_box=3.2);

    // Dãy Phải
    SignPost("KHU 3: BEP & NHA AN (13.5M)", [11.2, 2.0, 0], rot_z=90, width_box=4.2);
    SignPost("KHU 2: DAI LUC GIAC (12.0M)", [11.2, 16.5, 0], rot_z=90, width_box=4.2);
    SignPost("KHU 1: NHA 3 GIAN BAC BO (11.5M)", [11.2, 27.5, 0], rot_z=90, width_box=4.6);

    // Dãy Trái
    SignPost("KHU 4: NHA KHACH (12.0M)", [6.8, 2.0, 0], rot_z=-90, width_box=4.0);
    SignPost("KHU 5: AO CA (5.0M)", [6.8, 13.5, 0], rot_z=-90, width_box=3.0);
    SignPost("KHU 6: VUON CAY (16.0M)", [6.8, 20.0, 0], rot_z=-90, width_box=3.4);
    SignPost("KHU 7: QUY DAT DU TRU (4.0M)", [6.8, 34.5, 0], rot_z=-90, width_box=4.2);
}

// KHỞI CHẠY MÔ HÌNH CHÍNH
KhuNhaDongHo();
