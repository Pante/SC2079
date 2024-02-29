package com.example.mdp_group_14;

import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentPagerAdapter;

import java.util.ArrayList;

public class SectionsPagerAdapter extends FragmentPagerAdapter {
    private final ArrayList<Fragment> fragmentArrayList = new ArrayList<>();
    private final ArrayList<String> fragmentTitle = new ArrayList<>();


    public SectionsPagerAdapter(FragmentManager fm, int behaviour) {
        super(fm,behaviour);
    }

    @Override
    public Fragment getItem(int position) {
        return fragmentArrayList.get(position);
    }

    @Nullable
    @Override
    public CharSequence getPageTitle(int position) {
        return fragmentTitle.get(position);
    }

    @Override
    public int getCount() {
        return fragmentArrayList.size();
    }

    public void addFragment(Fragment fm, String title){
        fragmentArrayList.add(fm);
        fragmentTitle.add(title);
    }
}
