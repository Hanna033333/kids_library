const fs = require('fs');
const data = JSON.parse(fs.readFileSync('diagnosis.json', 'utf8'));

console.log('=== TIME INFO ===');
console.log(`Week: ${data.time_info.week_number}`);
console.log(`Age offset: ${data.time_info.age_offset}`);
console.log(`Research offset: ${data.time_info.research_offset}`);
console.log();

console.log('=== AGE GROUPS ===');
Object.entries(data.age_groups).forEach(([name, info]) => {
    console.log(`\n${name}:`);
    console.log(`  Total: ${info.total_count}`);
    console.log(`  In range: ${info.books_in_range}`);
    console.log(`  Has data: ${info.has_data}`);
    console.log(`  Offset exceeds total: ${info.offset_exceeds_total}`);
    if (info.sample_books && info.sample_books.length > 0) {
        console.log('  Sample:');
        info.sample_books.forEach(b => console.log(`    - ${b.id}: ${b.title}`));
    }
});

console.log('\n=== RESEARCH COUNCIL ===');
const rc = data.research_council;
console.log(`Total: ${rc.total_count}`);
console.log(`In range: ${rc.books_in_range}`);
console.log(`Has data: ${rc.has_data}`);

console.log('\n=== SONGPA LIBRARY ===');
const sp = data.songpa_library;
console.log(`Total: ${sp.total_count}`);
console.log(`Has data: ${sp.has_data}`);
