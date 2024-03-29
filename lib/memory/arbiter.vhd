library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity arbiter is
  port (
    clk       : in  std_ulogic;
    sreset    : in  std_ulogic;
    s_araddr  : in  std_ulogic_vector;
    s_arid    : in  std_ulogic_vector;
    s_arvalid : in  std_ulogic_vector;
    s_arready : out std_ulogic_vector;
    s_rdata   : out std_ulogic_vector;
    s_rid     : out std_logic_vector;
    s_rvalid  : out std_ulogic_vector;
    s_rready  : in  std_ulogic_vector;
    s_awaddr  : in  std_ulogic_vector;
    s_wready  : out std_ulogic_vector;
    s_wvalid  : in  std_ulogic_vector;
    s_wdata   : in  std_ulogic_vector;
    s_wid     : in  std_ulogic_vector;
    s_bready  : in  std_ulogic_vector;
    s_bvalid  : out std_ulogic_vector;
    s_bid     : out std_ulogic_vector;
    m_araddr  : out std_ulogic_vector;
    m_arid    : out std_ulogic_vector;
    m_arvalid : out std_ulogic;
    m_arready : in  std_ulogic;
    m_rdata   : in  std_ulogic_vector;
    m_rid     : in  std_logic_vector;
    m_rvalid  : in  std_ulogic;
    m_rready  : out std_ulogic;
    m_awaddr  : out std_ulogic_vector;
    m_wready  : in  std_ulogic;
    m_wvalid  : out std_ulogic;
    m_wdata   : out std_ulogic_vector;
    m_wid     : out std_ulogic_vector;
    m_bready  : out std_ulogic;
    m_bvalid  : in  std_ulogic;
    m_bid     : in  std_ulogic_vector
    );
end entity arbiter;

architecture rtl of arbiter is

  constant c_size     : positive := s_arvalid'length;
  constant c_id_width : positive := m_rid'length;
  constant c_id_size  : positive := 2 ** c_id_width;

  type tag_t is record
    id    : std_ulogic_vector(0 to c_id_width - 1);
    grant : natural range 0 to c_size - 1;
  end record tag_t;

  type tag_array_t is array (0 to c_id_size - 1) of tag_t;

  function first(data : std_ulogic_vector)
    return natural is
    alias x : std_ulogic_vector(0 to data'length - 1) is data;
  begin
    for i in x'range loop
      if x(i) = '1' then
        return i;
      end if;
    end loop;
    return 0;
  end function first;

  function get(data  : std_ulogic_vector;
               grant : natural)
    return std_ulogic_vector is
    constant c_data_width : positive := data'length / c_size;
    alias x               : std_ulogic_vector(0 to data'length - 1) is data;
  begin
    return x(grant * c_data_width to (grant + 1) * c_data_width - 1);
  end function get;

  function drive_one (
    data         : std_ulogic;
    grant        : natural;
    c_data_width : positive)
    return std_ulogic_vector is
    variable x : std_ulogic_vector(0 to c_data_width - 1);
  begin
    x        := (others => '0');
    x(grant) := data;
    return x;
  end function drive_one;

  function copy_all (
    data                  : std_ulogic_vector;
    constant c_data_width : positive)
    return std_ulogic_vector is
    variable x : std_ulogic_vector(0 to c_data_width - 1);
  begin
    for i in 0 to c_size - 1 loop
      x(i*data'length to (i+1)*data'length - 1) := data;
    end loop;
    return x;
  end function copy_all;

  signal ar_tag_i : tag_array_t;
  signal ar_id_i  : natural range 0 to c_id_size - 1;
  signal r_id_i   : natural range 0 to c_id_size - 1;
  signal s_arid_i : std_ulogic_vector(0 to c_id_width - 1);
  signal s_rid_i  : std_ulogic_vector(0 to c_id_width - 1);

  signal w_tag_i : tag_array_t;
  signal w_id_i  : natural range 0 to c_id_size - 1;
  signal s_wid_i : std_ulogic_vector(0 to c_id_width - 1);

  signal b_id_i : natural range 0 to c_id_size - 1;

  signal ar_grant_i : integer range 0 to c_size - 1;
  signal r_grant_i  : integer range 0 to c_size - 1;
  signal w_grant_i  : integer range 0 to c_size - 1;
  signal b_grant_i  : integer range 0 to c_size - 1;

  signal ar_transfer_i : boolean;
  signal w_transfer_i  : boolean;

begin

  ar_grant_i <= first(s_arvalid);
  w_grant_i  <= first(s_wvalid);

  m_arvalid <= s_arvalid(ar_grant_i);
  m_wvalid  <= s_wvalid(w_grant_i);

  s_arready <= drive_one(m_arready, ar_grant_i, s_arready'length);
  s_wready  <= drive_one(m_wready, w_grant_i, s_wready'length);

  ar_transfer_i <= (m_arvalid = '1' and m_arready = '1');
  w_transfer_i  <= (m_wvalid = '1' and m_wready = '1');

  s_arid_i <= get(s_arid, ar_grant_i);

  process (clk) is
  begin
    if rising_edge(clk) then
      if ar_transfer_i then
        ar_id_i           <= (ar_id_i + 1) mod c_id_size;
        ar_tag_i(ar_id_i) <= (id => s_arid_i, grant => ar_grant_i);
      end if;
      if w_transfer_i then
        w_id_i          <= (w_id_i + 1) mod c_id_size;
        w_tag_i(w_id_i) <= (id => s_wid_i, grant => w_grant_i);
      end if;
    end if;
  end process;

  r_id_i    <= to_integer(unsigned(m_rid));
  r_grant_i <= ar_tag_i(r_id_i).grant;

  s_rdata  <= copy_all(m_rdata, s_rdata'length);
  s_rid_i  <= ar_tag_i(r_id_i).id;
  s_rid    <= copy_all(s_rid_i, s_rid'length);
  s_rvalid <= drive_one(m_rvalid, r_grant_i, s_rvalid'length);

  m_araddr <= get(s_araddr, ar_grant_i);
  m_arid   <= std_ulogic_vector(to_unsigned(ar_id_i, m_arid'length));
  m_rready <= s_rready(r_grant_i);

  m_awaddr <= get(s_awaddr, w_grant_i);
  m_wid    <= std_ulogic_vector(to_unsigned(w_id_i, m_wid'length));

  s_wid_i <= get(s_wid, w_grant_i);

  m_wdata  <= get(s_wdata, w_grant_i);

  b_id_i    <= to_integer(unsigned(m_bid));
  b_grant_i <= w_tag_i(b_id_i).grant;

  m_bready <= s_bready(b_grant_i);

  s_bvalid <= drive_one(m_bvalid, b_grant_i, s_bvalid'length);
  s_bid    <= copy_all(w_tag_i(b_id_i).id, s_bid'length);

end architecture rtl;
