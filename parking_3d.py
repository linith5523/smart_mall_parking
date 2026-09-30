import json
import streamlit as st
import streamlit.components.v1 as components


def create_parking_3d(parked_vehicles=None, selected_shape="Rectangle"):
    """
    Renders an interactive 2D Parking Area Layout.
    - Title text formatted in dark high-contrast indigo.
    - UI and canvas container styled with Light Purple background.
    - Slots color-coded: RED = Occupied, GREEN = Free.
    """
    if parked_vehicles is None:
        parked_vehicles = {}

    vehicles_json = json.dumps(parked_vehicles)
    shape_str = str(selected_shape).strip()

    two_d_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                padding: 16px;
                background-color: #f3e8ff; /* Light purple page background */
                color: #1e1b4b;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            .header-card {{
                background: #ffffff;
                border: 2px solid #d8b4fe;
                border-radius: 10px;
                padding: 12px 20px;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 2px 10px rgba(147, 51, 234, 0.1);
            }}
            .main-title {{
                font-size: 18px;
                font-weight: 700;
                color: #3b0764; /* Very dark purple for maximum readability */
            }}
            .shape-subtitle {{
                color: #7e22ce;
                font-weight: 800;
            }}
            .legend-item {{
                display: inline-flex;
                align-items: center;
                margin-left: 16px;
                font-size: 13px;
                font-weight: 600;
                color: #374151;
            }}
            .legend-box {{
                width: 14px;
                height: 14px;
                border-radius: 3px;
                margin-right: 6px;
            }}
            .free-box {{ background-color: #10b981; border: 1px solid #059669; }}
            .occupied-box {{ background-color: #ef4444; border: 1px solid #dc2626; }}
            
            #canvas-wrapper {{
                width: 100%;
                background: #ebd5ff; /* Light purple inner container background */
                border: 2px solid #d8b4fe;
                border-radius: 12px;
                padding: 20px;
                display: flex;
                justify-content: center;
                overflow: auto;
            }}
            canvas {{
                background-color: #1e293b;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            }}
        </style>
    </head>
    <body>
        <div class="header-card">
            <div class="main-title">
                🅿️ 2D Parking Area Layout — <span class="shape-subtitle">{shape_str}</span>
            </div>
            <div>
                <span class="legend-item"><span class="legend-box free-box"></span> Free (Green)</span>
                <span class="legend-item"><span class="legend-box occupied-box"></span> Occupied (Red)</span>
            </div>
        </div>

        <div id="canvas-wrapper">
            <canvas id="parkingCanvas" width="850" height="520"></canvas>
        </div>

        <script>
            const parkedVehicles = {vehicles_json};
            const layoutShape = "{shape_str}";

            const canvas = document.getElementById('parkingCanvas');
            const ctx = canvas.getContext('2d');

            const slots = [];

            function buildLayout() {{
                if (layoutShape.includes("L-Shape") || layoutShape.includes("L")) {{
                    for (let i = 0; i < 7; i++) {{
                        slots.push({{ id: `A-1-00${{i + 1}}`, x: 60 + (i * 85), y: 60, w: 70, h: 100 }});
                    }}
                    for (let i = 0; i < 6; i++) {{
                        slots.push({{ id: `B-1-00${{i + 1}}`, x: 680, y: 190 + (i * 50), w: 100, h: 40 }});
                    }}
                }} else if (layoutShape.includes("U-Shape") || layoutShape.includes("U")) {{
                    for (let i = 0; i < 6; i++) {{
                        slots.push({{ id: `A-1-00${{i + 1}}`, x: 60, y: 60 + (i * 50), w: 100, h: 40 }});
                    }}
                    for (let i = 0; i < 5; i++) {{
                        slots.push({{ id: `B-1-00${{i + 1}}`, x: 210 + (i * 85), y: 380, w: 70, h: 100 }});
                    }}
                    for (let i = 0; i < 6; i++) {{
                        slots.push({{ id: `C-1-00${{i + 1}}`, x: 680, y: 60 + (i * 50), w: 100, h: 40 }});
                    }}
                }} else {{
                    for (let i = 0; i < 8; i++) {{
                        slots.push({{ id: `A-1-00${{i + 1}}`, x: 60 + (i * 92), y: 70, w: 78, h: 120 }});
                    }}
                    for (let i = 0; i < 8; i++) {{
                        slots.push({{ id: `B-1-00${{i + 1}}`, x: 60 + (i * 92), y: 310, w: 78, h: 120 }});
                    }}
                }}
            }}

            buildLayout();

            function render() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 2;
                ctx.setLineDash([10, 10]);
                
                if (layoutShape.includes("L-Shape") || layoutShape.includes("L")) {{
                    ctx.beginPath();
                    ctx.moveTo(50, 180);
                    ctx.lineTo(650, 180);
                    ctx.lineTo(650, 480);
                    ctx.stroke();
                }} else if (layoutShape.includes("U-Shape") || layoutShape.includes("U")) {{
                    ctx.beginPath();
                    ctx.moveTo(180, 50);
                    ctx.lineTo(180, 360);
                    ctx.lineTo(650, 360);
                    ctx.lineTo(650, 50);
                    ctx.stroke();
                }} else {{
                    ctx.beginPath();
                    ctx.moveTo(40, 250);
                    ctx.lineTo(810, 250);
                    ctx.stroke();
                }}
                ctx.setLineDash([]);

                slots.forEach(slot => {{
                    const isOccupied = Boolean(parkedVehicles[slot.id]);
                    const vehicleData = parkedVehicles[slot.id];
                    const plateNum = (typeof vehicleData === 'object' && vehicleData !== null) 
                        ? (vehicleData.vehicle_number || 'PARKED') 
                        : (typeof vehicleData === 'string' ? vehicleData : 'PARKED');

                    // RED if Occupied, GREEN if Free
                    ctx.fillStyle = isOccupied ? "#ef4444" : "#10b981";
                    ctx.strokeStyle = isOccupied ? "#f87171" : "#34d399";
                    ctx.lineWidth = 2;

                    ctx.beginPath();
                    ctx.roundRect(slot.x, slot.y, slot.w, slot.h, 6);
                    ctx.fill();
                    ctx.stroke();

                    ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
                    ctx.lineWidth = 1;
                    ctx.strokeRect(slot.x + 3, slot.y + 3, slot.w - 6, slot.h - 6);

                    ctx.fillStyle = "#ffffff";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";

                    if (slot.w > slot.h) {{
                        ctx.font = "bold 11px sans-serif";
                        ctx.fillText(slot.id, slot.x + (slot.w / 2), slot.y + (slot.h / 2) - (isOccupied ? 8 : 0));
                        if (isOccupied) {{
                            ctx.font = "10px sans-serif";
                            ctx.fillStyle = "#fef08a";
                            ctx.fillText(plateNum, slot.x + (slot.w / 2), slot.y + (slot.h / 2) + 8);
                        }}
                    }} else {{
                        ctx.font = "bold 12px sans-serif";
                        ctx.fillText(slot.id, slot.x + (slot.w / 2), slot.y + (slot.h / 2) - (isOccupied ? 10 : 0));
                        if (isOccupied) {{
                            ctx.font = "11px sans-serif";
                            ctx.fillStyle = "#fef08a";
                            ctx.fillText(plateNum, slot.x + (slot.w / 2), slot.y + (slot.h / 2) + 10);
                        }}
                    }}
                }});
            }}

            render();
        </script>
    </body>
    </html>
    """

    components.html(two_d_code, height=630, scrolling=False)