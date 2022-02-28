//Compile: g++ decrypt.cpp frost@ubuntu:~$ g++ decrypt.cpp -lcryptopp

#include <cryptopp/rc6.h>
#include <cryptopp/default.h>
#include <cryptopp/cryptlib.h>
#include <cryptopp/osrng.h>
#include <cryptopp/hex.h>
#include <bits/stdc++.h>

using namespace std;
using namespace CryptoPP;
int main(int argc, char** argv) {
    if (argc != 2){return 1;}


byte keyData[] = {123, 183, 157, 144, 20, 89, 103, 28, 175, 70, 79, 37, 75, 34, 149, 16};
SecByteBlock key(keyData, sizeof(keyData));


byte iv[] = {120, 81, 24, 185, 215, 165, 116, 160, 173, 143, 122, 28, 127, 140, 183, 226};

string plain = "CBC Mode Test";
//string cipher, encoded, recovered;
string encoded, recovered;


std::ifstream fin(argv[1], ios::binary);
ostringstream ostrm;
ostrm << fin.rdbuf();
string cipher( ostrm.str() );


try
{
    CBC_Mode< RC6 >::Decryption d;
    d.SetKeyWithIV(key, key.size(), iv);

    // The StreamTransformationFilter removes
    //  padding as required.
    StringSource s(cipher, true, 
        new StreamTransformationFilter(d,
            new StringSink(recovered)
        ) // StreamTransformationFilter
    ); // StringSource

    cout << recovered << endl;
}
catch(const CryptoPP::Exception& e)
{
    cerr << e.what() << endl;
    exit(1);
}
}
