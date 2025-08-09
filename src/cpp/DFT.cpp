#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <cmath>
#include <sstream>
#include <string>
#include <algorithm>

struct FourierComponent {
    double re;
    double im;
    int freq; 
    double amp;
    double phase;
};

std::vector<std::complex<double>> readCSVComplex(const std::string& filename) {
    std::ifstream file(filename);
    std::string line;
    std::vector<std::complex<double>> data;
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir arquivo CSV: " << filename << std::endl;
        return data;
    }
    std::getline(file, line); // Pula header
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string x_str, y_str;
        if (!std::getline(ss, x_str, ',')) continue;
        if (!std::getline(ss, y_str, ',')) continue;
        try {
            double x = std::stod(x_str);
            double y = std::stod(y_str);
            data.emplace_back(x, y);
        } catch (...) {
            data.emplace_back(0.0, 0.0);
        }
    }
    return data;
}

void writeJSON(const std::vector<FourierComponent>& comps, const std::string& filename) {
    std::ofstream out(filename);
    out << "[\n";
    for (size_t i = 0; i < comps.size(); ++i) {
        const auto& c = comps[i];
        out << "  {\n";
        out << "    \"freq\": " << c.freq << ",\n";
        out << "    \"amp\": " << c.amp << ",\n";
        out << "    \"phase\": " << c.phase << ",\n";
        out << "    \"re\": " << c.re << ",\n";
        out << "    \"im\": " << c.im << "\n";
        out << "  }";
        if (i + 1 < comps.size()) out << ",";
        out << "\n";
    }
    out << "]\n";
}

std::vector<FourierComponent> computeDFT(const std::vector<std::complex<double>>& data) {
    int N = (int)data.size();
    const double TWO_PI = 2 * M_PI;
    std::vector<FourierComponent> result;
    result.reserve(N);

    for (int k = 0; k < N; ++k) {
        std::complex<double> sum(0.0, 0.0);
        for (int n = 0; n < N; ++n) {
            double angle = -TWO_PI * k * n / N;
            std::complex<double> exp_val(std::cos(angle), std::sin(angle));
            sum += data[n] * exp_val;
        }
        sum /= N; // Normaliza

        double amp = std::abs(sum);
        double phase = std::atan2(sum.imag(), sum.real());

        
        int freq;
        if (k <= N / 2) {
            freq = k;
        } else {
            freq = k - N;
        }

        result.push_back({sum.real(), sum.imag(), freq, amp, phase});
    }
    return result;
}

int main() {
    auto data = readCSVComplex("cpp/input.csv");
    if (data.empty()) {
        std::cerr << "Nenhum dado carregado.\n";
        return 1;
    }

    auto dft_components = computeDFT(data);

    // Ordena os componentes pela amplitude em ordem decrescente
    std::sort(dft_components.begin(), dft_components.end(), [](const FourierComponent& a, const FourierComponent& b) {
        return a.amp > b.amp;
    });

    writeJSON(dft_components, "cpp/output.json");
    std::cout << "DFT calculada, ordenada por amplitude e salva em output.json\n";
    return 0;
}
