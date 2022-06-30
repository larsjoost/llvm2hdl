
mod add;

fn main() {
   let x = add::add(4, 5);
   if x != 9 { 
      std::process::exit(1);
   }
}