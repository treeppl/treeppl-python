{ lib, runCommand, stdenv, nix-gitignore,
  tinyxxd, zip,
  tpplc-tmp-tar-gz,
}:

let
  distribution = "treeppl";
  version = "0.1";
  os =
    if stdenv.hostPlatform.isLinux then "linux" else
    if stdenv.hostPlatform.isDarwin then "macosx_11_0" else
      throw "Unsupported host OS";
  architecture =
    if stdenv.hostPlatform.isx86_64 then "x86_64" else
    if stdenv.hostPlatform.isAarch64 then "arm64" else
      throw "Unsupported host architecture";
  platform = "${os}_${architecture}";
  selfcontainedDir = lib.strings.removeSuffix ".tar.gz" tpplc-tmp-tar-gz.name;
  args = {
    buildInputs = [ tinyxxd zip ];
  };
in

runCommand "treeppl-python" args ''
  # Actual content we care about
  cp -r ${nix-gitignore.gitignoreSource [] ../..}/treeppl .
  chmod +w treeppl
  cp ${tpplc-tmp-tar-gz}/${tpplc-tmp-tar-gz.name} treeppl/${tpplc-tmp-tar-gz.name}
  substituteInPlace treeppl/base.py \
    --replace-fail "@DEPLOYED_BASENAME@" "${selfcontainedDir}"

  # Wheel stuff that's needed for it to be valid
  mkdir -p ${distribution}-${version}.dist-info

  ## The METADATA file
  cat > ${distribution}-${version}.dist-info/METADATA <<METADATA-FILE
  Metadata-Version: 2.1
  Name: ${distribution}
  Version: ${version}
  Summary:
  Home-page: https://github.com/treeppl/treeppl-python
  Author: Jan Kudlicka
  Author-email: github@kudlicka.eu
  Supported-Platform: ${platform}
  Requires-Dist: numpy
  METADATA-FILE

  ## The WHEEL file
  cat > ${distribution}-${version}.dist-info/WHEEL <<WHEEL-FILE
  Wheel-Version: 1.0
  Generator: manual
  Root-Is-Purelib: false
  Tag: py3-none-any
  WHEEL-FILE

  ## The RECORD file
  for f in $(find * -type f); do
    echo -n $f, >> ${distribution}-${version}.dist-info/RECORD
    # via https://stackoverflow.com/questions/55904261/how-the-hash-in-record-file-of-a-wheel-package-is-constructed
    sha256sum < $f | awk '{print $1}' | xxd -r -p | base64 | tr +/ -_ | cut -c -43 | tr -d '\n' >>${distribution}-${version}.dist-info/RECORD
    echo -n , >> ${distribution}-${version}.dist-info/RECORD
    wc -c < $f >> ${distribution}-${version}.dist-info/RECORD
  done

  mkdir $out
  zip -r $out/${distribution}-${version}-py3-none-${platform}.whl *
''
