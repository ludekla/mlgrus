#include <iostream>
#include <fstream>
#include <string>
#include <regex>
#include <vector>
#include <memory>
#include <map>

using std::string;
using std::cout;
using std::endl;
using std::vector;

class Candidate {
    private:
        string level;
        string lang;
        bool tweets;
        bool phd;
    public:
        bool didwell;
        Candidate(string Level = "", string Lang = "") : level(Level), lang(Lang) {}
        ~Candidate() { cout << "oh no: "; print(); cout << "dying ..." << endl; }
        string Level() const { return level; }
        void Tweets(bool tws) { tweets = tws; }
        void PhD(bool ph) { phd = ph; }
        void print() const;
};

void Candidate::print() const {
    cout << "Candidate(level: " << level << ", lang: " << lang;
    cout << ", tweets: " << tweets << ", phd: " << phd << ")" << endl;
}

using CandidatePtr = std::unique_ptr<Candidate>;

vector<double> clsprobs(vector<bool> & vec) {
    double total = vec.size();
    std::map<bool, int> count;
    for (auto el : vec) {
        count[el] += 1;
    }
    vector<double> probs(count.size());
    int i = 0;
    for (auto iter = count.begin(); iter != count.end(); iter++) {
        probs[i++] = iter->second / total; 
    }
    return probs;
}

int main() {

    std::vector<CandidatePtr> cands;
    std::ifstream fin("cands.csv");
    std::string line;

    std::regex pat(R"(\s*,\s*)");

    std::getline(fin, line);
    while (fin.good()) {
        std::getline(fin, line);
        std::cout << line << std::endl;
        std::sregex_token_iterator csv(line.begin(), line.end(), pat, -1), end;
        string level {*csv++};
        string lang {*csv++};
        auto cand = std::make_unique<Candidate>(level, lang); 
        cand->Tweets(*csv++ == "1");
        cand->PhD(*csv++ == "1");
        cand->didwell = (*csv++ == "1");
        cand->print();
        cands.push_back(std::move(cand));
    }
    int ct = 0;
    vector<bool> vec(cands.size());
    for (auto & c : cands) {
        c->print();
        vec[ct++] = c->didwell;
    }
    vector<double> ps = clsprobs(vec);
    cout << "[ ";
    for (auto p : ps) { cout << p << " "; }
    cout << "]" << endl;
    std::cout << "that's it." << std::endl;
 }