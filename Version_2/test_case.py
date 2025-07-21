import pytest
from test_normalize import normalize_line

@pytest.mark.parametrize("inp, expected", [
    ("123 cm", 
     "một trăm hai mươi ba xen ti mét."),
    
    ("2km", 
     "hai kí lô mét."),
    
    ("10km3",
     "mười kí lô mét khối."),
    
    ("1000m2",
     "một nghìn mét vuông."),
    
    ("Sunhouse Inverter 1 HP SHR-AW09IC650",
     "Sunhouse Inverter một ếch pi ét ếch a ây đắp liu chín ai si sáu trăm năm mươi."),
    
    ("ngày 5/7/2025", 
     "ngày năm tháng bảy năm hai nghìn không trăm hai mươi lăm."),
    
    ("15kg", 
     "mười lăm kí lô gam."),
    
    ("3-5 cm", 
     "ba năm xen ti mét."),
    
    ("3cm-5cm", 
     "ba xen ti mét đến năm xen ti mét."),
    
    # Political division
    ("q.1",
     "quận một."),
    
    ("p.5",
     "phường năm."),
    
    ("h.2",
     "huyện hai."),
    
    # Street (prefix + số / hoặc -)
    ("đường 3/2",
     "đường ba , hai."),
    
    ("đường 15-3",
     "đường mười lăm ba."),
    
    ("hẻm 12-34",
     "hẻm mười hai ba mươi tư."),
    
    # Office (prefix + số / hoặc -)
    ("VP 12/3", 
     "văn phòng mười hai , ba."),
    
    ("văn phòng 5-6",
     "văn phòng năm sáu."),
    
    # Code number (chỉ số–số, không chứa chữ cái)
    ("123-456",
     "một trăm hai mươi ba bốn trăm năm mươi sáu."),
    
    ("2020/21",
     "hai nghìn không trăm hai mươi , hai mươi mốt."),
    
    # Không phải address → giữ nguyên
    ("Covid19",
     "Covid mười chín."),
    ("Bp12",
     "bê pê mười hai."),
    
    # Đơn vị đo
    ("m", "mờ."),                    
    ("1m", "một mét."),
    ("cm", "xê mờ."),
    ("3cm", "ba xen ti mét."),
    ("dm", "dê mờ."),
    ("2dm", "hai đề xi mét."),

    # Viết tắt đặc biệt
    ("knockwurstlmht",
     "knockwurstlmht."),     # Không bị thay vì không phải token riêng biệt

    # Số, tiền, phần trăm
    ("100$", "một trăm đô la."),
    ("1000€", "một nghìn ê rô."),
    ("110000£", "một trăm mười nghìn bảng."),
    ("15%", "mười lăm phần trăm."),
    ("20$", "hai mươi đô la."),
    ("123Ω", "một trăm hai mươi ba ôm."),

    # Ngày tháng năm, định dạng số, ngày lễ
    ("8/3 là ngày quốc tế phụ nữ",
     "tám , ba là ngày quốc tế phụ nữ."),
    ("ngày 8/3 là ngày quốc tế phụ nữ",
     "ngày tám tháng ba là ngày quốc tế phụ nữ."),
    
    ("25/12/2020",
     "hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi."),
    
    ("1/2024",
     "một , hai nghìn không trăm hai mươi tư."),
    
    ("2023", 
     "hai nghìn không trăm hai mươi ba."),
    ("từ 7:30AM - 5:30PM",
     "từ bảy giờ ba mươi ây em đến năm giờ ba mươi bi em."),
    ("từ ngày 3/1/2021 - 2/2/2023, từ tháng 3/2020 - 4/2020, từ 7:30 AM - 5:00 PM", 
     "từ ngày ba tháng một năm hai nghìn không trăm hai mươi mốt hai tháng hai năm hai nghìn không trăm hai mươi ba , từ tháng ba năm hai nghìn không trăm hai mươi đến tháng bốn năm hai nghìn không trăm hai mươi , từ bảy giờ ba mươi ây em đến năm giờ bi em."),
    ("từ 01/03-05/03, Ngày 5.3 đến 15.3, Từ 10/12 - 20/12",
     "từ một tháng ba đến năm tháng ba , ngày năm tháng ba đến mười lăm tháng ba , từ mười tháng mười hai đến hai mươi tháng mười hai."),
    ("từ 5-12.07, Ngày 01-31/12, Từ 3-15/4",
     "từ năm đến mười hai tháng bảy , ngày một đến ba mươi mốt tháng mười hai , từ ba đến mười lăm tháng bốn."),
    ("từ 1-12/2023, Tháng 01-6.2024, từ 5 - 11/2022",
     "từ một đến tháng mười hai năm hai nghìn không trăm hai mươi ba , tháng một đến tháng sáu năm hai nghìn không trăm hai mươi tư , từ năm đến tháng mười một năm hai nghìn không trăm hai mươi hai."),
    ("từ 3/1/2021 - 2/2/2023, từ 3/2020 - 4/2020, từ 7:30 AM - 5:00 PM",
     "từ ba tháng một năm hai nghìn không trăm hai mươi mốt hai tháng hai năm hai nghìn không trăm hai mươi ba , từ ba năm hai nghìn không trăm hai mươi đến tháng bốn năm hai nghìn không trăm hai mươi , từ bảy giờ ba mươi ây em đến năm giờ bi em."),
    

    # email, web, điện thoại
    ("email: abc@gmail.com",
     "email ây bi si a còng giy meo chấm com."),
    
    ("website: www.example.com",
     "website vê kép vê kép vê kép chấm e ích a mờ pê lờ e chấm com."),
    
    ("số điện thoại: 0912345678",
     "số điện thoại không chín một hai ba bốn năm sáu bảy tám."),

    # Test giữ nguyên số 4 chữ số (năm)
    ("Năm 2016",
     "Năm hai nghìn không trăm mười sáu."),

    # Phần trăm, đơn vị tiền tệ
    ("Giá sản phẩm là 10,5€, 10.5$, thuế 5%",
     "Giá sản phẩm là mười phẩy năm ê rô , mười phẩy năm đô la , thuế năm phần trăm."),
    
    ("Thế kỉ XX",
     "Thế kỉ hai mươi."),

    # Thử số + đơn vị đo viết liền
    ("15cm", "mười lăm xen ti mét."),
    ("100dm", "một trăm đề xi mét."),
    ("LG Inverter, FV1409S2V, WW10T534DBX/SV", 
     "eo giy Inverter , ép vi một nghìn bốn trăm linh chín ét hai vê , đắp liu đắp liu mười T năm trăm ba mươi tư đi bi ít xuyệt ét vê." ),

    # Thử dấu câu
    ("1m, 2cm và 3dm.", "một mét , hai xen ti mét và ba đề xi mét."),
    
    ("1000000", "một triệu."),
    ("10000000", "mười triệu."),
    ("100000000", "một trăm triệu."),
    ("1000000000", "một tỷ."),
    ("10000000000", "mười tỷ."),
    ("100000000000", "một trăm tỷ."),
    ("10$", "mười đô la."),
    ("50%", "năm mươi phần trăm."), 
    ("123Ω", "một trăm hai mươi ba ôm."),
    
    ("Có phải tháng 12/2020 đã có vaccine phòng ngừa Covid-19 xmz ?", 
     "Có phải tháng mười hai năm hai nghìn không trăm hai mươi đã có vaccine phòng ngừa Covid mười chín ích mờ giét."),
    ("Thịt gà 96%, muối 1%, tiêu đen 1%, bột nghệ, đường, chất làm ẩm, chất điều chỉnh độ acid, chất chống oxy hóa.",
    "Thịt gà chín mươi sáu phần trăm , muối một phần trăm , tiêu đen một phần trăm , bột nghệ , đường , chất làm ẩm , chất điều chỉnh độ acid , chất chống ô xi hóa."),
    
    # Mã bảo hành
    ("Nhập mã bảo hành: BH20250630.", 
     "Nhập mã bảo hành bi ếch hai không hai năm không sáu ba không."),
    
    # Serial number
    ("Serial máy: SNX123456789.", 
     "Serial máy ét en ít một hai ba bốn năm sáu bảy tám chín."),
    
    # Mã giảm giá
    ("Áp dụng mã giảm giá: GIAM50, giảm ngay 50.000đ", 
     "Áp dụng mã giảm giá GIAM năm mươi , giảm ngay năm mươi nghìn đồng."),
    
    # Giá thập phân
    ("Giá ưu đãi chỉ còn 3.990.500đ.", 
     "Giá ưu đãi chỉ còn ba triệu chín trăm chín mươi nghìn năm trăm đồng."),
    
    # Mã sản phẩm dạng lạ
    ("Mã sản phẩm: ABC01-23A.", 
     "Mã sản phẩm ây bi si một hai mươi ba a."),
    
    # Thời hạn bảo hành
    ("Bảo hành 18 tháng hoặc 1.5 năm.", 
     "Bảo hành mười tám tháng hoặc một phẩy năm năm."),
    
    # Website
    ("Truy cập website: www.dienmayabc.com", 
     "Truy cập website vê kép vê kép vê kép chấm dê i e nờ mờ a i a bê xê chấm com."),
    
    # Email hỗ trợ
    ("Gửi mail tới: hotro@dienmayabc.com", 
     "Gửi mail tới ếch âu ti a âu a còng đi ai i en em ây quai ây bi si chấm si âu em."),
    
    # % ưu đãi
    ("Giảm giá 10% cho đơn hàng đầu tiên.", 
     "Giảm giá mười phần trăm cho đơn hàng đầu tiên."),
    
    # Giá có số lẻ/thập phân
    ("Giá khuyến mãi chỉ 4.599.000đ.", 
     "Giá khuyến mãi chỉ bốn triệu năm trăm chín mươi chín nghìn đồng."),
    
    # Số điện thoại hotline dạng mới
    ("Liên hệ: 1800 6868.", 
     "Liên hệ một tám không không sáu tám sáu tám."),
    
    # Mã đơn hàng online
    ("Mã đơn hàng: ORD-090624-XYZ.", 
     "Mã đơn hàng âu a đi không chín không sáu hai bốn ích i giét."),
    
    # Số serial in trên máy
    ("Số serial: A1B3C23D.", 
     "Số serial A một B ba C hai mươi ba dê."),
    
    # Mã bảo hành có chữ và số
    ("Vui lòng nhập mã: ABC12345.", 
     "Vui lòng nhập mã ây bi si một hai ba bốn năm."),
    
    # Số và đơn vị thập phân
    ("Khối lượng 2.5kg.", 
     "Khối lượng hai phẩy năm kí lô gam."),
    
    # Số model phổ biến
    ("Model: FV1409S2V.", 
     "Model ép vi một nghìn bốn trăm linh chín ét hai vê."),
    
    # Trạng thái order
    ("Đơn hàng số: 101010 đã giao.", 
     "Đơn hàng số một trăm linh một nghìn không trăm mười đã giao."),
    
    # Giá sản phẩm có dấu phẩy và đơn vị tiền tệ khác
    ("Giá chỉ từ 2999999$", 
     "Giá chỉ từ hai triệu chín trăm chín mươi chín nghìn chín trăm chín mươi chín đô la."),

    # Số seri có ký tự đặc biệt (slash)
    ("Serial: AHVTF/RW12UG.", 
     "Serial ây ếch vi ti ép xuyệt a đắp liu mười hai u giê."),

    # Số điện thoại có dấu gạch
    ("Hotline hỗ trợ: 090-123-4567.", 
     "Hotline hỗ trợ không chín không một hai ba bốn năm sáu bảy."),

    # Số tiền có dấu chấm ngăn cách ngàn
    ("Tổng giá trị: 5.000.000đ.",
     "Tổng giá trị năm triệu đồng."),

    # Ngày tháng năm dạng DD/MM/YYYY
    ("Ngày mua: 01/07/2024.", 
     "Ngày mua một tháng bảy năm hai nghìn không trăm hai mươi tư."),

    # Đơn vị đo ngắn
    ("Chiều dài 30cm, rộng 20cm.", 
     "Chiều dài ba mươi xen ti mét , rộng hai mươi xen ti mét."),

    # Email domain lạ
    ("Liên hệ: user_xyz@abc.io.", 
     "Liên hệ diu ét i a ít quai giét a còng ây bi si chấm ai âu."),

    # Website có https
    ("Tham khảo tại https://www.abc.com.vn", 
     "Tham khảo tại hát tê tê pê ét xuyệt xuyệt vê kép vê kép vê kép chấm a bê xê chấm com chấm vê nờ."),

    # Mã hàng hóa toàn số
    ("Mã hàng: 456789123.", 
     "Mã hàng bốn trăm năm mươi sáu triệu bảy trăm tám mươi chín nghìn một trăm hai mươi ba."),
])
def test_normalize_line(inp, expected):
    options = {"punc": False, "unknown": False, "lower": False, "rule": False}
    assert normalize_line(inp, options) == expected
