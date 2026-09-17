import os
import ssl
import urllib.parse
import pandas as pd
from flask import Flask, render_template_string, request

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

# ID Spreadsheet
SHEET_ID_UTAMA = "1FKYLB_YYtXgB83ydpvhlzxEESmzkiMhBiz5KiZPRqag"
SHEET_ID_ALUMNI = "1q_CLTnSBZi21F50iZFJEzFtABZqC-DWr"

def get_sheet_url(sheet_name, sheet_id=SHEET_ID_UTAMA):
    encoded = urllib.parse.quote(sheet_name)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Rumah Qur'an</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .card-stat { border-radius: 12px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .table-card { border-radius: 12px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .nav-tabs .nav-link { font-weight: 600; color: #495057; border: none; border-bottom: 3px solid transparent; }
        .nav-tabs .nav-link.active { color: #198754; border: none; border-bottom: 3px solid #198754; background: transparent; }
    </style>
</head>
<body class="p-4">
    <div class="container-fluid">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
            <div>
                <h2 class="fw-bold text-success mb-0">📖 Dashboard santri Rumah Quran Bina Santri Indonesia</h2>
                <p class="text-muted mb-0">Tahun ajaran 2026-2027</p>
            </div>
            <span class="badge bg-success p-2 fs-6">Tersinkronisasi Online</span>
        </div>

        <!-- Metric Cards -->
        <div class="row g-3 mb-4">
            <div class="col-md-2 col-sm-6">
                <div class="card card-stat bg-white p-3 h-100">
                    <div class="text-muted small">TOTAL CABANG</div>
                    <div class="h4 fw-bold text-dark mb-0">{{ total_cabang }} Lokasi</div>
                </div>
            </div>
            <div class="col-md-2 col-sm-6">
                <div class="card card-stat bg-white p-3 h-100">
                    <div class="text-muted small">TOTAL SANTRI AKTIF</div>
                    <div class="h4 fw-bold text-primary mb-0">{{ total_santri }} Santri</div>
                </div>
            </div>
            <div class="col-md-2 col-sm-6">
                <div class="card card-stat bg-white p-3 h-100">
                    <div class="text-muted small">TOTAL KAPASITAS</div>
                    <div class="h4 fw-bold text-secondary mb-0">{{ total_kapasitas }} Santri</div>
                </div>
            </div>
            <div class="col-md-2 col-sm-6">
                <div class="card card-stat bg-white p-3 h-100">
                    <div class="text-muted small">TINGKAT KETERISIAN</div>
                    <div class="h4 fw-bold text-success mb-0">{{ okupansi }}%</div>
                </div>
            </div>
            <div class="col-md-2 col-sm-6">
                <div class="card card-stat bg-white p-3 h-100">
                    <div class="text-muted small">TOTAL TASMI'</div>
                    <div class="h4 fw-bold text-info mb-0">{{ total_tasmi }} Santri</div>
                </div>
            </div>
            <div class="col-md-2 col-sm-6">
                <div class="card card-stat bg-white p-3 h-100">
                    <div class="text-muted small">TOTAL ALUMNI</div>
                    <div class="h4 fw-bold text-danger mb-0">{{ total_alumni }} Alumni</div>
                </div>
            </div>
        </div>

        <!-- Bagian Grafik & Profil Cabang -->
        <div class="row g-3 mb-4">
            <div class="col-lg-5">
                <div class="card card-stat bg-white p-3 h-100">
                    <h6 class="fw-bold mb-1">Grafik Santri vs Kapasitas (Rumah Qur'an)</h6>
                    <small class="text-muted mb-2 d-block">Cabang asrama tahfidz reguler</small>
                    <canvas id="cabangChart" height="150"></canvas>
                </div>
            </div>
            
            <div class="col-lg-3">
                <div class="card card-stat bg-white p-3 h-100 border-start border-warning border-4">
                    <h6 class="fw-bold mb-1">RBQ Cikupa</h6>
                    <small class="text-muted mb-2 d-block">Rumah Belajar Qur'an (Non-Asrama)</small>
                    <canvas id="cikupaChart" height="150"></canvas>
                </div>
            </div>

            <div class="col-lg-4">
                <div class="card card-stat bg-white p-3 h-100">
                    <h6 class="fw-bold mb-2">Daftar cabang RQ</h6>
                    <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                        <table class="table table-sm table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Informasi RQ</th>
                                    <th class="text-center">Santri</th>
                                    <th class="text-center">Kapasitas</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for r in profil_data %}
                                <tr>
                                    <td class="py-2">
                                        <div class="fw-semibold text-dark">{{ r.get('Rumah Tahfidz', '-') }}</div>
                                        <div class="small text-muted mb-1">👤 PIC: {{ r.get('Kontak Pembina', '-') }}</div>
                                        {% if r.get('Alamat_Clean') and r.get('Alamat_Clean') != '-' %}
                                        <div class="small text-secondary" style="font-size: 0.8rem; line-height: 1.25;">📍 {{ r.get('Alamat_Clean') }}</div>
                                        {% endif %}
                                        {% if r.get('Maps_Link') and r.get('Maps_Link') != '-' and 'http' in r.get('Maps_Link') %}
                                        <div class="mt-1">
                                            <a href="{{ r.get('Maps_Link') }}" target="_blank" class="badge bg-light text-primary border text-decoration-none py-1 px-2">
                                                🗺️ Buka Google Maps
                                            </a>
                                        </div>
                                        {% endif %}
                                    </td>
                                    <td class="text-center"><span class="badge bg-primary">{{ r.get('Jumlah Santri', 0) }}</span></td>
                                    <td class="text-center">{{ r.get('Kapasitas Rumah Qur’an', 0) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab Navigasi -->
        <div class="card table-card bg-white p-4">
            <ul class="nav nav-tabs mb-4" id="dashboardTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link {% if active_tab == 'santri' or not active_tab %}active{% endif %}" id="santri-tab" data-bs-toggle="tab" data-bs-target="#santri-content" type="button" role="tab">
                        👥 Data Santri ({{ santri_total }})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link {% if active_tab == 'rata2' %}active{% endif %}" id="rata2-tab" data-bs-toggle="tab" data-bs-target="#rata2-content" type="button" role="tab">
                        📊 Rata-Rata Hafalan ({{ rata2_data | length }})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link {% if active_tab == 'prestasi' %}active{% endif %}" id="prestasi-tab" data-bs-toggle="tab" data-bs-target="#prestasi-content" type="button" role="tab">
                        🏆 Data Santri Berprestasi ({{ total_prestasi_filtered }})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link {% if active_tab == 'tasmi' %}active{% endif %}" id="tasmi-tab" data-bs-toggle="tab" data-bs-target="#tasmi-content" type="button" role="tab">
                        📜 Data Tasmi' Santri ({{ total_tasmi_filtered }})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link {% if active_tab == 'alumni' %}active{% endif %}" id="alumni-tab" data-bs-toggle="tab" data-bs-target="#alumni-content" type="button" role="tab">
                        🎓 Data Alumni ({{ total_alumni_filtered }})
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="dashboardTabContent">
                <!-- Tab 1: Database Santri -->
                <div class="tab-pane fade {% if active_tab == 'santri' or not active_tab %}show active{% endif %}" id="santri-content" role="tabpanel">
                    <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-2 mb-md-0 text-muted">Daftar Santri Aktif</h6>
                        <form method="get" class="d-flex gap-2">
                            <input type="hidden" name="tab" value="santri">
                            <select name="cabang" class="form-select form-select-sm" onchange="this.form.submit()">
                                <option value="">Semua Cabang</option>
                                {% for c in cabang_list %}
                                <option value="{{ c }}" {% if selected_cabang == c %}selected{% endif %}>{{ c }}</option>
                                {% endfor %}
                            </select>
                            <input type="text" name="cari" class="form-control form-control-sm" placeholder="Cari nama santri..." value="{{ query_cari }}">
                            <button type="submit" class="btn btn-sm btn-success">Cari</button>
                            {% if query_cari or selected_cabang %}
                            <a href="/?tab=santri" class="btn btn-sm btn-outline-secondary">Reset</a>
                            {% endif %}
                        </form>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-striped table-hover align-middle">
                            <thead class="table-dark text-center">
                                <tr>
                                    <th style="width: 5%;">No</th>
                                    <th style="width: 20%;" class="text-start">Nama Santri</th>
                                    <th style="width: 12%;">Total Hafalan</th>
                                    <th style="width: 10%;">Tasmi'</th>
                                    <th style="width: 10%;">Cabang</th>
                                    <th style="width: 8%;">Grade</th>
                                    <th style="width: 10%;">Status</th>
                                    <th style="width: 9%;">Gender</th>
                                    <th style="width: 8%;">Kelas</th>
                                    <th style="width: 8%;">Tahun Masuk</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for s in santri_data %}
                                <tr>
                                    <td class="text-center">{{ loop.index }}</td>
                                    <td class="fw-bold text-start">{{ s.get('Nama_Clean', '-') }}</td>
                                    <td class="text-center">
                                        {% if s.get('Hafalan_Terbaru') and s.get('Hafalan_Terbaru') != '-' %}
                                        <span class="badge bg-success fs-6">{{ s.get('Hafalan_Terbaru') }}</span>
                                        {% else %}
                                        <span class="text-muted">-</span>
                                        {% endif %}
                                    </td>
                                    <td class="text-center">
                                        {% if s.get('Tasmi_Status') and s.get('Tasmi_Status') != '-' %}
                                        <span class="badge bg-warning text-dark fs-6">{{ s.get('Tasmi_Status') }}</span>
                                        {% else %}
                                        <span class="text-muted">-</span>
                                        {% endif %}
                                    </td>
                                    <td class="text-center"><span class="badge bg-secondary">{{ s.get('Cabang', '-') }}</span></td>
                                    <td class="text-center"><span class="badge bg-light text-dark border">{{ s.get('Grade_Clean', '-') }}</span></td>
                                    <td class="text-center"><span class="badge bg-info text-dark">{{ s.get('Status_Clean', '-') }}</span></td>
                                    <td class="text-center">{{ s.get('Gender_Clean', '-') }}</td>
                                    <td class="text-center fw-semibold">{{ s.get('Kelas_Clean', '-') }}</td>
                                    <td class="text-center">{{ s.get('Tahun_Clean', '-') }}</td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="10" class="text-center py-4 text-muted">Tidak ada data santri yang cocok.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Tab 2: Rata-Rata Hafalan per Cabang RQ -->
                <div class="tab-pane fade {% if active_tab == 'rata2' %}show active{% endif %}" id="rata2-content" role="tabpanel">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <h6 class="fw-bold mb-0 text-muted">RATA-RATA CAPAIAN HAFALAN PER RUMAH QUR'AN</h6>
                            <small class="text-success fw-semibold">Pembaruan data otomatis mengikuti bulan terbaru yang terisi</small>
                        </div>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-bordered table-striped table-hover align-middle">
                            <thead class="table-dark text-center">
                                <tr>
                                    <th style="width: 8%;">NO</th>
                                    <th style="width: 40%;" class="text-start">CABANG RUMAH QUR'AN</th>
                                    <th style="width: 26%;">BULAN TERAKHIR TERISI</th>
                                    <th style="width: 26%;">RATA-RATA HAFALAN</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for r in rata2_data %}
                                <tr>
                                    <td class="text-center">{{ loop.index }}</td>
                                    <td class="fw-bold text-start">{{ r.get('Cabang', '-') }}</td>
                                    <td class="text-center"><span class="badge bg-info text-dark fs-6">{{ r.get('Bulan_Terbaru', '-') }}</span></td>
                                    <td class="text-center"><span class="badge bg-success fs-6">{{ r.get('Nilai_Rata2', '-') }} Juz</span></td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="4" class="text-center py-4 text-muted">Data rata-rata hafalan belum tersedia.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Tab 3: Data Santri Berprestasi -->
                <div class="tab-pane fade {% if active_tab == 'prestasi' %}show active{% endif %}" id="prestasi-content" role="tabpanel">
                    <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-2 mb-md-0 text-muted">DATA SANTRI BERPRESTASI</h6>
                        <form method="get" class="d-flex gap-2">
                            <input type="hidden" name="tab" value="prestasi">
                            <select name="cabang_prestasi" class="form-select form-select-sm" onchange="this.form.submit()">
                                <option value="">Semua Cabang</option>
                                {% for c in cabang_list_prestasi %}
                                <option value="{{ c }}" {% if selected_cabang_prestasi == c %}selected{% endif %}>{{ c }}</option>
                                {% endfor %}
                            </select>
                            <input type="text" name="cari_prestasi" class="form-control form-control-sm" placeholder="Cari nama/penghargaan..." value="{{ query_cari_prestasi }}">
                            <button type="submit" class="btn btn-sm btn-warning text-dark fw-semibold">Cari</button>
                            {% if query_cari_prestasi or selected_cabang_prestasi %}
                            <a href="/?tab=prestasi" class="btn btn-sm btn-outline-secondary">Reset</a>
                            {% endif %}
                        </form>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-bordered table-striped table-hover align-middle">
                            <thead class="table-dark text-center">
                                <tr>
                                    <th style="width: 5%;">NO</th>
                                    <th style="width: 17%;">Nama</th>
                                    <th style="width: 12%;">Rumah Qur’an</th>
                                    <th style="width: 25%;">Penghargaan</th>
                                    <th style="width: 15%;">Lomba</th>
                                    <th style="width: 11%;">Tingkat</th>
                                    <th style="width: 8%;">Bulan</th>
                                    <th style="width: 7%;">Tahun</th>
                                    <th style="width: 10%;">Link Foto</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for p in prestasi_data %}
                                <tr>
                                    <td class="text-center">{{ loop.index }}</td>
                                    <td class="fw-bold">{{ p.get('Nama', '-') }}</td>
                                    <td><span class="badge bg-success">{{ p.get('Rumah_Quran', '-') }}</span></td>
                                    <td class="fw-semibold text-primary">{{ p.get('Penghargaan', '-') }}</td>
                                    <td>{{ p.get('Lomba', '-') }}</td>
                                    <td>{{ p.get('Tingkat', '-') }}</td>
                                    <td class="text-center">{{ p.get('Bulan', '-') }}</td>
                                    <td class="text-center">{{ p.get('Tahun', '-') }}</td>
                                    <td class="text-center">
                                        {% if p.get('Link_Foto') and p.get('Link_Foto') != '-' and 'http' in p.get('Link_Foto') %}
                                        <a href="{{ p.get('Link_Foto') }}" target="_blank" class="btn btn-sm btn-primary py-0 px-2">Lihat Foto</a>
                                        {% else %}
                                        -
                                        {% endif %}
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="9" class="text-center py-4 text-muted">Belum ada data prestasi yang tercatat.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Tab 4: Data Tasmi' Santri -->
                <div class="tab-pane fade {% if active_tab == 'tasmi' %}show active{% endif %}" id="tasmi-content" role="tabpanel">
                    <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-2 mb-md-0 text-muted">DATA TASMI' SANTRI TA 2026-2027</h6>
                        <form method="get" class="d-flex gap-2">
                            <input type="hidden" name="tab" value="tasmi">
                            <select name="cabang_tasmi" class="form-select form-select-sm" onchange="this.form.submit()">
                                <option value="">Semua Cabang</option>
                                {% for c in cabang_list_tasmi %}
                                <option value="{{ c }}" {% if selected_cabang_tasmi == c %}selected{% endif %}>{{ c }}</option>
                                {% endfor %}
                            </select>
                            <input type="text" name="cari_tasmi" class="form-control form-control-sm" placeholder="Cari santri..." value="{{ query_cari_tasmi }}">
                            <button type="submit" class="btn btn-sm btn-info text-white fw-semibold">Cari</button>
                            {% if query_cari_tasmi or selected_cabang_tasmi %}
                            <a href="/?tab=tasmi" class="btn btn-sm btn-outline-secondary">Reset</a>
                            {% endif %}
                        </form>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-bordered table-striped table-hover align-middle">
                            <thead class="table-dark text-center">
                                <tr>
                                    <th style="width: 8%;">NO</th>
                                    <th style="width: 35%;">NAMA SANTRI</th>
                                    <th style="width: 18%;">JUMLAH JUZ</th>
                                    <th style="width: 20%;">TGL TASMI</th>
                                    <th style="width: 19%;">RQ (CABANG)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for t in tasmi_data %}
                                <tr>
                                    <td class="text-center">{{ loop.index }}</td>
                                    <td class="fw-bold">{{ t.get('Nama', '-') }}</td>
                                    <td class="text-center"><span class="badge bg-primary fs-6">{{ t.get('Jumlah_Juz', '-') }} Juz</span></td>
                                    <td class="text-center">{{ t.get('Tgl_Tasmi', '-') }}</td>
                                    <td class="text-center"><span class="badge bg-success fs-6">{{ t.get('RQ', '-') }}</span></td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="5" class="text-center py-4 text-muted">Belum ada data tasmi' yang cocok.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Tab 5: Data Alumni -->
                <div class="tab-pane fade {% if active_tab == 'alumni' %}show active{% endif %}" id="alumni-content" role="tabpanel">
                    <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-2 mb-md-0 text-muted">DATA ALUMNI RUMAH QUR'AN</h6>
                        <form method="get" class="d-flex gap-2">
                            <input type="hidden" name="tab" value="alumni">
                            <select name="cabang_alumni" class="form-select form-select-sm" onchange="this.form.submit()">
                                <option value="">Semua Rumah Tahfidz</option>
                                {% for c in cabang_list_alumni %}
                                <option value="{{ c }}" {% if selected_cabang_alumni == c %}selected{% endif %}>{{ c }}</option>
                                {% endfor %}
                            </select>
                            <input type="text" name="cari_alumni" class="form-control form-control-sm" placeholder="Cari nama/aktivitas..." value="{{ query_cari_alumni }}">
                            <button type="submit" class="btn btn-sm btn-danger fw-semibold">Cari</button>
                            {% if query_cari_alumni or selected_cabang_alumni %}
                            <a href="/?tab=alumni" class="btn btn-sm btn-outline-secondary">Reset</a>
                            {% endif %}
                        </form>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-bordered table-striped table-hover align-middle">
                            <thead class="table-dark text-center">
                                <tr>
                                    <th style="width: 4%;">No</th>
                                    <th style="width: 16%;" class="text-start">Nama Alumni</th>
                                    <th style="width: 10%;">Asal</th>
                                    <th style="width: 14%;">TTL</th>
                                    <th style="width: 9%;">Bergabung</th>
                                    <th style="width: 10%;">Tahun Wisuda</th>
                                    <th style="width: 11%;">Rumah Tahfidz</th>
                                    <th style="width: 16%;">Aktivitas Saat Ini</th>
                                    <th style="width: 10%;">No. Telepon</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for a in alumni_data %}
                                <tr>
                                    <td class="text-center">{{ loop.index }}</td>
                                    <td class="fw-bold text-start">{{ a.get('Nama', '-') }}</td>
                                    <td class="text-center">{{ a.get('Asal', '-') }}</td>
                                    <td class="small">{{ a.get('TTL', '-') }}</td>
                                    <td class="text-center small">{{ a.get('Bergabung', '-') }}</td>
                                    <td class="text-center"><span class="badge bg-secondary">{{ a.get('Tahun_Wisuda', '-') }}</span></td>
                                    <td class="text-center"><span class="badge bg-success">{{ a.get('Rumah_Tahfidz', '-') }}</span></td>
                                    <td>{{ a.get('Aktivitas', '-') }}</td>
                                    <td class="text-center small">{{ a.get('No_Tlp', '-') }}</td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="9" class="text-center py-4 text-muted">Belum ada data alumni yang cocok.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const ctxRQ = document.getElementById('cabangChart').getContext('2d');
        new Chart(ctxRQ, {
            type: 'bar',
            data: {
                labels: {{ chart_labels | tojson }},
                datasets: [
                    { label: 'Jumlah Santri', data: {{ chart_santri | tojson }}, backgroundColor: 'rgba(25, 135, 84, 0.85)' },
                    { label: 'Kapasitas', data: {{ chart_kapasitas | tojson }}, backgroundColor: 'rgba(108, 117, 125, 0.4)' }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } }
            }
        });

        const ctxCikupa = document.getElementById('cikupaChart').getContext('2d');
        new Chart(ctxCikupa, {
            type: 'bar',
            data: {
                labels: ['RBQ Cikupa'],
                datasets: [
                    { label: 'Jumlah Santri', data: [{{ cikupa_santri }}], backgroundColor: 'rgba(13, 110, 253, 0.85)' },
                    { label: 'Kapasitas', data: [{{ cikupa_kapasitas }}], backgroundColor: 'rgba(108, 117, 125, 0.4)' }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } }
            }
        });
    </script>
</body>
</html>
"""

def extract_rata2_sheet():
    """Membaca sheet 'rata2 hafalan' dan mengambil rata-rata bulan terbaru tiap cabang"""
    rata2_list = []
    url = get_sheet_url('rata2 hafalan', sheet_id=SHEET_ID_UTAMA)
    try:
        raw = pd.read_csv(url, header=None)
        
        # Temukan baris header bulan
        header_idx = None
        for idx, r in raw.head(6).iterrows():
            line = " ".join(r.dropna().astype(str).tolist()).lower()
            if "juli" in line and "agustus" in line:
                header_idx = idx
                break
                
        if header_idx is not None:
            df = pd.read_csv(url, skiprows=header_idx)
        else:
            df = pd.read_csv(url)

        df.columns = [str(c).strip() for c in df.columns]

        bulan_order = ['juli', 'agustus', 'september', 'oktober', 'november', 'desember', 'januari', 'februari', 'maret', 'april', 'mei', 'juni']
        month_cols = []
        for b in bulan_order:
            found = next((c for c in df.columns if c.lower() == b or b in c.lower()), None)
            if found:
                month_cols.append((b.capitalize(), found))

        # Telusuri baris RATA-RATA tiap cabang
        current_rq = "-"
        for idx, row in df.iterrows():
            first_val = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if first_val and first_val.lower() not in ['rq', 'nan', '', 'no', 'nama']:
                if 'rata' not in first_val.lower():
                    current_rq = first_val

            row_str = " ".join(row.dropna().astype(str).tolist()).lower()
            if "rata-rata" in row_str or "rata2" in row_str or "rata" in row_str:
                # Cari nilai bulan terbaru dari kanan ke kiri
                val_terbaru = "-"
                nama_bulan_terbaru = "-"
                
                for b_name, m_col in reversed(month_cols):
                    v = row.get(m_col)
                    if pd.notna(v):
                        v_str = str(v).strip()
                        # Abaikan nilai kosong, strip, atau error excel #DIV/0!
                        if v_str and v_str.lower() not in ['nan', '-', ''] and not v_str.startswith('#'):
                            try:
                                num = float(v_str.replace(',', '.'))
                                val_terbaru = f"{num:.2f}"
                            except Exception:
                                val_terbaru = v_str
                            nama_bulan_terbaru = b_name
                            break
                
                cabang_name = current_rq if current_rq != "-" else f"Cabang {len(rata2_list) + 1}"
                rata2_list.append({
                    'Cabang': cabang_name.replace('RQ ', '').strip(),
                    'Bulan_Terbaru': nama_bulan_terbaru,
                    'Nilai_Rata2': val_terbaru
                })
    except Exception as e:
        print(f"Error memuat rata2 hafalan: {e}")
        
    return rata2_list

def extract_profil_sheet():
    profil_url = get_sheet_url('Profil', sheet_id=SHEET_ID_UTAMA)
    try:
        raw_df = pd.read_csv(profil_url, header=None)
        header_idx = None
        for idx, r in raw_df.head(6).iterrows():
            line = " ".join(r.dropna().astype(str).tolist()).lower()
            if "rumah tahfidz" in line or "alamat" in line:
                header_idx = idx
                break
                
        if header_idx is not None:
            df = pd.read_csv(profil_url, skiprows=header_idx)
        else:
            df = pd.read_csv(profil_url)

        df.columns = [str(c).strip() for c in df.columns]

        rt_col = next((c for c in df.columns if 'rumah tahfidz' in c.lower()), None)
        alamat_col = next((c for c in df.columns if 'alamat' in c.lower()), None)
        maps_col = next((c for c in df.columns if 'google maps' in c.lower() or 'maps' in c.lower()), None)

        if rt_col:
            df = df.dropna(subset=[rt_col]).copy()
            df = df[~df[rt_col].astype(str).str.strip().str.lower().isin(['rumah tahfidz', '', 'nan', 'total', 'jumlah'])]
            df['Alamat_Clean'] = df[alamat_col].fillna('-').astype(str).str.strip() if alamat_col else '-'
            df['Maps_Link'] = df[maps_col].fillna('-').astype(str).str.strip() if maps_col else '-'
            return df
    except Exception as e:
        print(f"Error memuat profil: {e}")
        
    return pd.DataFrame()

def extract_alumni_sheet():
    alumni_df = pd.DataFrame()
    url = get_sheet_url('alumni rq', sheet_id=SHEET_ID_ALUMNI)
    try:
        raw = pd.read_csv(url, header=None)
        header_idx = None
        for idx, r in raw.head(8).iterrows():
            line = " ".join(r.dropna().astype(str).tolist()).lower()
            if "nama" in line and ("wisuda" in line or "tahfidz" in line or "asal" in line):
                header_idx = idx
                break
                
        if header_idx is not None:
            df = pd.read_csv(url, skiprows=header_idx)
        else:
            df = pd.read_csv(url)

        df.columns = [str(c).strip() for c in df.columns]

        nama_c = next((c for c in df.columns if c.lower() in ['nama', 'nama alumni']), None)
        asal_c = next((c for c in df.columns if 'asal' in c.lower()), None)
        ttl_c = next((c for c in df.columns if any(k in c.lower() for k in ['tempat tanggal lahir', 'ttl', 'lahir'])), None)
        gabung_c = next((c for c in df.columns if 'bergabung' in c.lower() or 'masuk' in c.lower()), None)
        wisuda_c = next((c for c in df.columns if 'wisuda' in c.lower() or 'lulus' in c.lower()), None)
        rt_c = next((c for c in df.columns if 'tahfidz' in c.lower() or 'cabang' in c.lower() or 'rq' in c.lower()), None)
        aktivitas_c = next((c for c in df.columns if 'aktivitas' in c.lower() or 'kegiatan' in c.lower()), None)
        tlp_c = next((c for c in df.columns if any(k in c.lower() for k in ['tlp', 'telp', 'hp', 'kontak', 'wa'])), None)

        if nama_c:
            clean_df = df.dropna(subset=[nama_c]).copy()
            clean_df = clean_df[~clean_df[nama_c].astype(str).str.strip().str.lower().isin(
                ['nama', 'total', 'jumlah', '', 'nan', 'no']
            )]
            
            clean_df['Nama'] = clean_df[nama_c].astype(str).str.strip()
            clean_df['Asal'] = clean_df[asal_c].fillna('-').astype(str).str.strip() if asal_c else '-'
            clean_df['TTL'] = clean_df[ttl_c].fillna('-').astype(str).str.strip() if ttl_c else '-'
            clean_df['Bergabung'] = clean_df[gabung_c].fillna('-').astype(str).str.strip() if gabung_c else '-'
            clean_df['Tahun_Wisuda'] = clean_df[wisuda_c].fillna('-').astype(str).str.strip() if wisuda_c else '-'
            clean_df['Rumah_Tahfidz'] = clean_df[rt_c].fillna('-').astype(str).str.replace('Rumah Tahfidz ', '').str.strip() if rt_c else '-'
            clean_df['Aktivitas'] = clean_df[aktivitas_c].fillna('-').astype(str).str.strip() if aktivitas_c else '-'
            clean_df['No_Tlp'] = clean_df[tlp_c].fillna('-').astype(str).str.replace('.0', '', regex=False).str.strip() if tlp_c else '-'
            
            alumni_df = clean_df[['Nama', 'Asal', 'TTL', 'Bergabung', 'Tahun_Wisuda', 'Rumah_Tahfidz', 'Aktivitas', 'No_Tlp']]
    except Exception as e:
        print(f"Error memuat alumni: {e}")
        
    return alumni_df

def extract_total_hafalan_map():
    url = get_sheet_url('total hafalan', sheet_id=SHEET_ID_UTAMA)
    hafalan_dict = {}
    tasmi_dict = {}
    try:
        raw = pd.read_csv(url, header=None)
        header_idx = None
        for idx, r in raw.head(8).iterrows():
            line = " ".join(r.dropna().astype(str).tolist()).lower()
            if "nama" in line and ("juli" in line or "bulan" in line or "tasmi" in line or "kelas" in line):
                header_idx = idx
                break
                
        if header_idx is not None:
            df = pd.read_csv(url, skiprows=header_idx)
        else:
            df = pd.read_csv(url)

        df.columns = [str(c).strip() for c in df.columns]
        nama_c = next((c for c in df.columns if c.lower() in ['nama', 'nama santri']), None)
        if not nama_c:
            nama_c = next((c for c in df.columns if 'nama' in c.lower() and 'ayah' not in c.lower()), None)
            
        tasmi_col = next((c for c in df.columns if 'tasmi' in c.lower()), None)
        bulan_order = ['juli', 'agustus', 'september', 'oktober', 'november', 'desember', 'januari', 'februari', 'maret', 'april', 'mei', 'juni']
        
        month_cols = []
        for b in bulan_order:
            found = next((c for c in df.columns if c.lower() == b or b in c.lower()), None)
            if found:
                month_cols.append(found)

        if nama_c:
            clean_df = df.dropna(subset=[nama_c]).copy()
            clean_df = clean_df[~clean_df[nama_c].astype(str).str.strip().str.lower().isin(
                ['nama', 'total', 'jumlah', '', 'nan', 'no', 'kelas']
            )]
            
            for _, row in clean_df.iterrows():
                nama = str(row[nama_c]).strip()
                if not nama or nama.lower() == 'nan':
                    continue
                    
                hafalan_terbaru = '-'
                for col in reversed(month_cols):
                    val = row.get(col)
                    if pd.notna(val):
                        val_str = str(val).strip()
                        if val_str and val_str.lower() not in ['nan', '-', '']:
                            hafalan_terbaru = val_str
                            break
                            
                tasmi_val = '-'
                if tasmi_col and pd.notna(row.get(tasmi_col)):
                    t_str = str(row.get(tasmi_col)).strip()
                    if t_str and t_str.lower() not in ['nan', '']:
                        tasmi_val = t_str
                            
                norm_nama = "".join(nama.lower().split())
                hafalan_dict[norm_nama] = hafalan_terbaru
                hafalan_dict[nama.lower()] = hafalan_terbaru
                tasmi_dict[norm_nama] = tasmi_val
                tasmi_dict[nama.lower()] = tasmi_val
                
    except Exception as e:
        print(f"Error memuat total hafalan: {e}")
        
    return hafalan_dict, tasmi_dict

def extract_santri_sheet(sheet_name, hafalan_map, tasmi_map):
    url = get_sheet_url(sheet_name, sheet_id=SHEET_ID_UTAMA)
    try:
        raw_df = pd.read_csv(url, header=None)
    except Exception:
        return None

    header_row_idx = None
    for idx, row in raw_df.head(10).iterrows():
        row_str = " ".join(row.dropna().astype(str).tolist()).lower()
        if "nama" in row_str:
            header_row_idx = idx
            break

    if header_row_idx is not None:
        df = pd.read_csv(url, skiprows=header_row_idx)
    else:
        df = pd.read_csv(url)

    df.columns = [str(c).strip() for c in df.columns]
    nama_col = next((c for c in df.columns if c.lower() in ['nama', 'nama santri', 'nama lengkap']), None)
    if not nama_col:
        for c in df.columns:
            if 'nama' in c.lower() and 'ayah' not in c.lower() and 'ibu' not in c.lower():
                nama_col = c
                break
    if not nama_col:
        return None

    df_clean = df.dropna(subset=[nama_col]).copy()
    df_clean = df_clean[~df_clean[nama_col].astype(str).str.strip().str.lower().isin(
        ['nama', 'nama santri', 'grade', '', 'total', 'jumlah', 'bsi maslahat', 'bsi']
    )]
    
    df_clean['Nama_Clean'] = df_clean[nama_col].astype(str).str.strip()
    
    def get_val_from_map(name, source_map):
        norm = "".join(name.lower().split())
        if norm in source_map:
            return source_map[norm]
        if name.lower() in source_map:
            return source_map[name.lower()]
        for k, v in source_map.items():
            if k in norm or norm in k:
                return v
        return '-'

    df_clean['Hafalan_Terbaru'] = df_clean['Nama_Clean'].apply(lambda n: get_val_from_map(n, hafalan_map))
    df_clean['Tasmi_Status'] = df_clean['Nama_Clean'].apply(lambda n: get_val_from_map(n, tasmi_map))
    
    grade_col = next((c for c in df.columns if 'grade' in c.lower()), None)
    if not grade_col:
        grade_col = next((c for c in df.columns if 'kelas' in c.lower()), None)
    df_clean['Grade_Clean'] = df_clean[grade_col].fillna('-') if grade_col else '-'
    
    kelas_col_j = None
    if len(df.columns) > 9:
        candidate_j = df.columns[9]
        if 'kelas' in candidate_j.lower() or 'grade' not in candidate_j.lower():
            kelas_col_j = candidate_j
            
    if not kelas_col_j:
        for c in df.columns:
            if 'kelas' in c.lower() and c != grade_col:
                kelas_col_j = c
                break

    df_clean['Kelas_Clean'] = df_clean[kelas_col_j].fillna('-') if kelas_col_j else '-'
    status_col = next((c for c in df.columns if 'status' in c.lower()), None)
    df_clean['Status_Clean'] = df_clean[status_col].fillna('-') if status_col else '-'
    gender_col = next((c for c in df.columns if 'kelamin' in c.lower() or 'gender' in c.lower() or c.lower() == 'jk'), None)
    df_clean['Gender_Clean'] = df_clean[gender_col].fillna('-') if gender_col else '-'
    thn_col = next((c for c in df.columns if 'tahun' in c.lower() or 'masuk' in c.lower()), None)
    if thn_col:
        df_clean['Tahun_Clean'] = pd.to_numeric(df_clean[thn_col], errors='coerce').fillna(0).astype(int).replace(0, '-')
    else:
        df_clean['Tahun_Clean'] = '-'

    clean_cabang_name = sheet_name.replace('RQ ', '')
    df_clean['Cabang'] = clean_cabang_name
    return df_clean

def extract_prestasi_sheet():
    possible_prestasi_sheets = ['prestasi', 'Prestasi', 'Data Prestasi', 'Prestasi Santri', 'Capaian Santri']
    prestasi_df = pd.DataFrame()
    for s_name in possible_prestasi_sheets:
        try:
            url = get_sheet_url(s_name, sheet_id=SHEET_ID_UTAMA)
            raw = pd.read_csv(url, header=None)
            header_idx = None
            for idx, r in raw.head(10).iterrows():
                row_text = " ".join(r.dropna().astype(str).tolist()).lower()
                if "penghargaan" in row_text or ("nama" in row_text and "lomba" in row_text):
                    header_idx = idx
                    break
            
            if header_idx is not None:
                df = pd.read_csv(url, skiprows=header_idx)
            else:
                df = pd.read_csv(url)

            df.columns = [str(c).strip() for c in df.columns]
            nama_c = next((c for c in df.columns if c.lower() in ['nama', 'nama santri']), None)
            rq_c = next((c for c in df.columns if any(k in c.lower() for k in ['rumah qur', 'qur’an', 'cabang'])), None)
            penghargaan_c = next((c for c in df.columns if 'penghargaan' in c.lower()), None)
            lomba_c = next((c for c in df.columns if 'lomba' in c.lower()), None)
            tingkat_c = next((c for c in df.columns if 'tingkat' in c.lower()), None)
            bulan_c = next((c for c in df.columns if 'bulan' in c.lower()), None)
            tahun_c = next((c for c in df.columns if 'tahun' in c.lower()), None)
            foto_c = next((c for c in df.columns if any(k in c.lower() for k in ['foto', 'link', 'drive'])), None)

            if not penghargaan_c and len(df.columns) > 3:
                penghargaan_c = df.columns[3]
            
            if nama_c:
                clean_df = df.dropna(subset=[nama_c]).copy()
                clean_df = clean_df[~clean_df[nama_c].astype(str).str.strip().str.lower().isin(
                    ['nama', 'total', 'jumlah', '', 'nan', 'data santri berprestasi']
                )]
                
                clean_df['Nama'] = clean_df[nama_c].astype(str).str.strip()
                clean_df['Rumah_Quran'] = clean_df[rq_c].fillna('-').astype(str).str.strip() if rq_c else '-'
                clean_df['Penghargaan'] = clean_df[penghargaan_c].fillna('-').astype(str).str.strip() if penghargaan_c else '-'
                clean_df['Lomba'] = clean_df[lomba_c].fillna('-').astype(str).str.strip() if lomba_c else '-'
                clean_df['Tingkat'] = clean_df[tingkat_c].fillna('-').astype(str).str.strip() if tingkat_c else '-'
                clean_df['Bulan'] = clean_df[bulan_c].fillna('-').astype(str).str.strip() if bulan_c else '-'
                clean_df['Tahun'] = clean_df[tahun_c].fillna('-').astype(str).str.strip() if tahun_c else '-'
                clean_df['Link_Foto'] = clean_df[foto_c].fillna('-').astype(str).str.strip() if foto_c else '-'
                prestasi_df = clean_df[['Nama', 'Rumah_Quran', 'Penghargaan', 'Lomba', 'Tingkat', 'Bulan', 'Tahun', 'Link_Foto']]
                break
        except Exception:
            continue
    return prestasi_df

def extract_tasmi_sheet():
    possible_names = ['data tasmi', 'Data Tasmi', 'tasmi', 'Tasmi']
    tasmi_df = pd.DataFrame()
    for s_name in possible_names:
        try:
            url = get_sheet_url(s_name, sheet_id=SHEET_ID_UTAMA)
            raw = pd.read_csv(url, header=None)
            header_idx = None
            for idx, r in raw.head(10).iterrows():
                line = " ".join(r.dropna().astype(str).tolist()).lower()
                if "nama santri" in line or "jumlah juz" in line:
                    header_idx = idx
                    break
            
            if header_idx is not None:
                df = pd.read_csv(url, skiprows=header_idx)
            else:
                df = pd.read_csv(url)

            df.columns = [str(c).strip() for c in df.columns]
            nama_c = next((c for c in df.columns if 'nama' in c.lower()), None)
            juz_c = next((c for c in df.columns if 'juz' in c.lower()), None)
            tgl_c = next((c for c in df.columns if 'tgl' in c.lower() or 'tanggal' in c.lower()), None)
            rq_c = next((c for c in df.columns if c.lower() == 'rq' or 'cabang' in c.lower()), None)

            if nama_c:
                clean_df = df.dropna(subset=[nama_c]).copy()
                clean_df = clean_df[~clean_df[nama_c].astype(str).str.strip().str.lower().isin(
                    ['nama', 'nama santri', 'total', 'jumlah', '', 'nan', 'data tasmi santri ta 2026-2027']
                )]
                clean_df['Nama'] = clean_df[nama_c].astype(str).str.strip()
                clean_df['Jumlah_Juz'] = clean_df[juz_c].fillna('-').astype(str).str.replace('.0', '', regex=False).str.strip() if juz_c else '-'
                clean_df['Tgl_Tasmi'] = clean_df[tgl_c].fillna('-').astype(str).str.strip() if tgl_c else '-'
                clean_df['RQ'] = clean_df[rq_c].fillna('-').astype(str).str.strip() if rq_c else '-'
                tasmi_df = clean_df[['Nama', 'Jumlah_Juz', 'Tgl_Tasmi', 'RQ']]
                break
        except Exception:
            continue
    return tasmi_df

def load_online_data():
    profil_df = extract_profil_sheet()
    hafalan_map, tasmi_map = extract_total_hafalan_map()
    
    rq_sheets = ['RQ Parung', 'RQ Bogor', 'RQ Cimahi', 'RQ Semarang', 'RQ Solo', 'RQ Magetan', 'RQ Aceh']
    santri_list = []
    for s in rq_sheets:
        df_cabang = extract_santri_sheet(s, hafalan_map, tasmi_map)
        if df_cabang is not None and len(df_cabang) > 0:
            santri_list.append(df_cabang)
            
    all_santri = pd.concat(santri_list, ignore_index=True) if santri_list else pd.DataFrame()
    rata2_data = extract_rata2_sheet()
    prestasi_data = extract_prestasi_sheet()
    tasmi_data = extract_tasmi_sheet()
    alumni_data = extract_alumni_sheet()
    
    return profil_df, all_santri, rata2_data, prestasi_data, tasmi_data, alumni_data

@app.route('/')
def home():
    profil_df, all_santri, rata2_data, prestasi_df, tasmi_df, alumni_df = load_online_data()
    
    total_cabang = len(profil_df)
    total_santri = int(profil_df['Jumlah Santri'].sum()) if not profil_df.empty and 'Jumlah Santri' in profil_df.columns else 0
    total_kapasitas = int(profil_df['Kapasitas Rumah Qur’an'].sum()) if not profil_df.empty and 'Kapasitas Rumah Qur’an' in profil_df.columns else 0
    okupansi = round((total_santri / total_kapasitas * 100), 1) if total_kapasitas > 0 else 0
    total_prestasi = len(prestasi_df)
    total_tasmi = len(tasmi_df)
    total_alumni = len(alumni_df)
    
    active_tab = request.args.get('tab', 'santri')
    
    # Filter Santri
    selected_cabang = request.args.get('cabang', '')
    query_cari = request.args.get('cari', '')
    filtered_santri = all_santri.copy()
    if selected_cabang and not filtered_santri.empty:
        filtered_santri = filtered_santri[filtered_santri['Cabang'] == selected_cabang]
    if query_cari and not filtered_santri.empty:
        filtered_santri = filtered_santri[filtered_santri['Nama_Clean'].astype(str).str.contains(query_cari, case=False, na=False)]
    cabang_list = sorted(all_santri['Cabang'].unique()) if not all_santri.empty else []
    
    # Filter Prestasi
    selected_cabang_prestasi = request.args.get('cabang_prestasi', '')
    query_cari_prestasi = request.args.get('cari_prestasi', '')
    filtered_prestasi = prestasi_df.copy()
    if selected_cabang_prestasi and not filtered_prestasi.empty:
        filtered_prestasi = filtered_prestasi[filtered_prestasi['Rumah_Quran'] == selected_cabang_prestasi]
    if query_cari_prestasi and not filtered_prestasi.empty:
        m1 = filtered_prestasi['Nama'].astype(str).str.contains(query_cari_prestasi, case=False, na=False)
        m2 = filtered_prestasi['Penghargaan'].astype(str).str.contains(query_cari_prestasi, case=False, na=False)
        m3 = filtered_prestasi['Lomba'].astype(str).str.contains(query_cari_prestasi, case=False, na=False)
        filtered_prestasi = filtered_prestasi[m1 | m2 | m3]
    cabang_list_prestasi = sorted(prestasi_df['Rumah_Quran'].unique()) if not prestasi_df.empty else []
    
    # Filter Tasmi'
    selected_cabang_tasmi = request.args.get('cabang_tasmi', '')
    query_cari_tasmi = request.args.get('cari_tasmi', '')
    filtered_tasmi = tasmi_df.copy()
    if selected_cabang_tasmi and not filtered_tasmi.empty:
        filtered_tasmi = filtered_tasmi[filtered_tasmi['RQ'] == selected_cabang_tasmi]
    if query_cari_tasmi and not filtered_tasmi.empty:
        m1 = filtered_tasmi['Nama'].astype(str).str.contains(query_cari_tasmi, case=False, na=False)
        m2 = filtered_tasmi['Jumlah_Juz'].astype(str).contains(query_cari_tasmi, case=False, na=False)
        filtered_tasmi = filtered_tasmi[m1 | m2]
    cabang_list_tasmi = sorted(tasmi_df['RQ'].unique()) if not tasmi_df.empty else []
    
    # Filter Alumni
    selected_cabang_alumni = request.args.get('cabang_alumni', '')
    query_cari_alumni = request.args.get('cari_alumni', '')
    filtered_alumni = alumni_df.copy()
    if selected_cabang_alumni and not filtered_alumni.empty:
        filtered_alumni = filtered_alumni[filtered_alumni['Rumah_Tahfidz'] == selected_cabang_alumni]
    if query_cari_alumni and not filtered_alumni.empty:
        m_alumni1 = filtered_alumni['Nama'].astype(str).str.contains(query_cari_alumni, case=False, na=False)
        m_alumni2 = filtered_alumni['Aktivitas'].astype(str).contains(query_cari_alumni, case=False, na=False)
        m_alumni3 = filtered_alumni['Asal'].astype(str).contains(query_cari_alumni, case=False, na=False)
        filtered_alumni = filtered_alumni[m_alumni1 | m_alumni2 | m_alumni3]
    cabang_list_alumni = sorted(alumni_df['Rumah_Tahfidz'].unique()) if not alumni_df.empty else []

    # Pisahkan grafik RQ vs RBQ Cikupa
    labels_rq = []
    santri_rq = []
    kapasitas_rq = []
    cikupa_santri = 0
    cikupa_kapasitas = 0

    if not profil_df.empty and 'Rumah Tahfidz' in profil_df.columns:
        for _, row in profil_df.iterrows():
            nama_cabang = str(row.get('Rumah Tahfidz', ''))
            j_santri = int(row.get('Jumlah Santri', 0)) if pd.notna(row.get('Jumlah Santri')) else 0
            k_santri = int(row.get('Kapasitas Rumah Qur’an', 0)) if pd.notna(row.get('Kapasitas Rumah Qur’an')) else 0
            
            if 'cikupa' in nama_cabang.lower():
                cikupa_santri = j_santri
                cikupa_kapasitas = k_santri
            else:
                label_clean = nama_cabang.replace('Rumah Qur’an BSI ', '').replace('Rumah Belajar Qur’an ', '').strip()
                labels_rq.append(label_clean)
                santri_rq.append(j_santri)
                kapasitas_rq.append(k_santri)

    return render_template_string(
        HTML_TEMPLATE,
        total_cabang=total_cabang,
        total_santri=total_santri,
        total_kapasitas=total_kapasitas,
        total_prestasi=total_prestasi,
        total_tasmi=total_tasmi,
        total_alumni=total_alumni,
        okupansi=okupansi,
        profil_data=profil_df.to_dict(orient='records'),
        santri_data=filtered_santri.to_dict(orient='records'),
        santri_total=len(filtered_santri),
        rata2_data=rata2_data,
        prestasi_data=filtered_prestasi.to_dict(orient='records'),
        total_prestasi_filtered=len(filtered_prestasi),
        tasmi_data=filtered_tasmi.to_dict(orient='records'),
        total_tasmi_filtered=len(filtered_tasmi),
        alumni_data=filtered_alumni.to_dict(orient='records'),
        total_alumni_filtered=len(filtered_alumni),
        cabang_list=cabang_list,
        cabang_list_prestasi=cabang_list_prestasi,
        cabang_list_tasmi=cabang_list_tasmi,
        cabang_list_alumni=cabang_list_alumni,
        selected_cabang=selected_cabang,
        selected_cabang_prestasi=selected_cabang_prestasi,
        selected_cabang_tasmi=selected_cabang_tasmi,
        selected_cabang_alumni=selected_cabang_alumni,
        query_cari=query_cari,
        query_cari_prestasi=query_cari_prestasi,
        query_cari_tasmi=query_cari_tasmi,
        query_cari_alumni=query_cari_alumni,
        active_tab=active_tab,
        chart_labels=labels_rq,
        chart_santri=santri_rq,
        chart_kapasitas=kapasitas_rq,
        cikupa_santri=cikupa_santri,
        cikupa_kapasitas=cikupa_kapasitas
    )

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Aplikasi Dashboard Berjalan!")
    print("Buka browser dan akses: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(port=5000, debug=False)